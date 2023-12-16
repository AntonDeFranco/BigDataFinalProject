"""Functions to parse the historical data from OpenMeteo APIs."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import openmeteo_requests
import requests_cache
from openmeteo_sdk.WeatherApiResponse import VariablesWithTime
from retry_requests import retry

from constants import (
    BASE_OPENMETEO_URL,
    DEFAULT_DATA_DIR,
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE,
    SCHEMA,
)


def _date2datetime(dt: str) -> str:
    """Convert a date string to a datetime string."""
    try:
        dt_str = datetime.strptime(dt, "%Y-%m-%d")
        return dt_str
    except ValueError:
        raise ValueError(
            f"Invalid date format. Should be YYYY-MM-DD, but got {dt}"
        )


def request_data(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    out: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Request data from the OpenMeteo API.

    Args:
        lat (Optional[float], optional): Latitude for the location.
            If `None`, use the default latitude. Defaults to `None`.
        lon (Optional[float], optional): Longitude for the location.
            If `None`, use the default longitude. Defaults to `None`.
        start_date (Optional[str], optional): Start date for the data.
            The format should be "YYYY-MM-DD". Defaults to `None`.
        end_date (Optional[str], optional): End date for the data.
            The format should be "YYYY-MM-DD". Defaults to `None`.
        out (Optional[pd.DataFrame], optional): DataFrame to append the data
            to. Defaults to `None`.

    Returns:
        WeatherApiResponse: Response from the API.
    """
    if out is None:
        out = pd.DataFrame(columns=SCHEMA)
    assert isinstance(out, pd.DataFrame) and out.columns.tolist() == SCHEMA, (
        "Invalid data schema. Expected: "
        f"{SCHEMA}, but got: {out.columns.tolist()}"
    )

    # Initialize the client for OpenMeteo
    cache_session = requests_cache.CachedSession(".cache", expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo_client = openmeteo_requests.Client(session=retry_session)

    # Preprocess start and end date
    if start_date:
        start_date = _date2datetime(start_date)
    else:
        start_date = datetime.now() - timedelta(days=365)
    if end_date:
        end_date = _date2datetime(end_date)

    # Fetch data
    response: VariablesWithTime = openmeteo_client.weather_api(
        url=BASE_OPENMETEO_URL,
        params={
            "latitude": lat or DEFAULT_LATITUDE,
            "longitude": lon or DEFAULT_LONGITUDE,
            "start_date": "2022-01-01",
            "end_date": "2023-12-16",
            "hourly": [
                "temperature_2m",
                "apparent_temperature",
                "pressure_msl",
                "relative_humidity_2m",
                "rain",
                "snowfall",
                "cloud_cover",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
            ],
            "wind_speed_unit": "ms",
            "timeformat": "unixtime",
            "timezone": "America/Chicago",
        },
    )[0].Hourly()

    df = {
        "timestamp": pd.date_range(
            start=pd.to_datetime(
                datetime.fromtimestamp(response.Time()).isoformat()
            ),
            end=pd.to_datetime(
                datetime.fromtimestamp(response.TimeEnd()).isoformat()
            ),
            freq=pd.Timedelta(seconds=response.Interval()),
            inclusive="left",
        )
    }
    df["longitude"] = lon or DEFAULT_LONGITUDE
    df["latitude"] = lat or DEFAULT_LATITUDE
    for i, scheme in enumerate(SCHEMA[3:]):
        df[scheme] = response.Variables(i).ValuesAsNumpy()

    out = pd.concat([out, pd.DataFrame(df)], ignore_index=True)
    out.reset_index(inplace=True)
    if "index" in out.columns:
        out.drop(columns=["index"], inplace=True)

    return out


def main() -> None:
    """Entry point for parsing the historical weather data."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--latitude",
        type=float,
        required=False,
        help="Latitude for the location",
    )
    parser.add_argument(
        "--longitude",
        type=float,
        required=False,
        help="Longitude for the location",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        required=False,
        help="Start date for the data",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        required=False,
        help="End date for the data",
    )
    parser.add_argument(
        "--out",
        type=str,
        required=False,
        default=Path(DEFAULT_DATA_DIR, "history.csv"),
        help="Output file for the data",
    )
    args = parser.parse_args()

    # Fetch the data
    if args.start_date is None:
        start_date = datetime.now() - timedelta(days=365)
        start_date = start_date.strftime("%Y-%m-%d")
        args.start_date = start_date
    if args.end_date is None:
        end_date = datetime.now()
        end_date = end_date.strftime("%Y-%m-%d")
        args.end_date = end_date
    if args.out and Path(args.out).exists():
        out = pd.read_csv(args.out)
    else:
        out = None
    weather_data = request_data(
        lat=args.latitude,
        lon=args.longitude,
        start_date=args.start_date,
        end_date=args.end_date,
        out=out,
    )

    # Save the data
    assert isinstance(weather_data, pd.DataFrame)
    weather_data.to_csv(args.out, index=False)


if __name__ == "__main__":
    main()
