"""Functions to parse the current data from OpenWeatherMap APIs."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Literal, Optional

import pandas as pd
import pytz
import requests

from constants import (
    BASE_OPENWEATHER_URL,
    DEFAULT_DATA_DIR,
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE,
    SCHEMA,
)


def request_data(
    api_key: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    mode: Optional[Literal["xml", "html"]] = None,
    units: Literal["standard", "metric", "imperial"] = "metric",
    lang: str = "en",
) -> Dict[str, Any]:
    """Request data from the OpenWeatherMap API.

    Args:
        api_key (str): API key for OpenWeatherMap.
        lat (Optional[float], optional): Latitude for the location.
            If `None`, use the default latitude. Defaults to `None`.
        lon (Optional[float], optional): Longitude for the location.
            If `None`, use the default longitude. Defaults to `None`.
        mode (Optional[Literal["xml", "html"]], optional): Response format.
            Either "xml" or "html". If `None`, use JSON. Defaults to `None`.
        units (Literal["standard", "metric", "imperial"], optional): Units for
            the response. Defaults to "standard".
        lang (str, optional): Language for the response. Defaults to "en".
            Learn more at :url:`https://openweathermap.org/current#multi`.

    Returns:
        Dict[str, Any]: Response from the API.

    Raises:
        RuntimeError: If the API returns an error.
    """
    url = BASE_OPENWEATHER_URL + "&".join(
        [
            f"lat={lat or DEFAULT_LATITUDE}",
            f"lon={lon or DEFAULT_LONGITUDE}",
            f"appid={api_key}",
            f"mode={mode}" if mode else "",
            f"units={units}",
            f"lang={lang}",
        ]
    )
    response = requests.get(url).json()
    if response["cod"] == 200:
        return response
    else:
        raise RuntimeError(
            f"Failed to fetch weather data: {response['message']}"
        )


def process_data(
    weather_data: Dict[str, Any], out: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """Process the weather data into a dataframe.

    Args:
        weather_data (Dict[str, Any]): Weather data from the API.
    """
    if out is None:
        out = pd.DataFrame(columns=SCHEMA)
    assert out.columns.tolist() == SCHEMA, "Schema mismatch."

    # Add the current weather data to the dataframe
    utc_now = datetime.utcnow()
    current_time = (
        utc_now.replace(tzinfo=pytz.utc)
        .astimezone(pytz.timezone("America/Chicago"))
        .replace(microsecond=0)
    )
    out.loc[len(out)] = [
        pd.to_datetime(current_time),
        weather_data["coord"]["lon"],
        weather_data["coord"]["lat"],
        weather_data["main"]["temp"],
        weather_data["main"]["feels_like"],
        weather_data["main"]["pressure"],
        weather_data["main"]["humidity"],
        weather_data["rain"]["1h"] if "rain" in weather_data else 0.0,
        weather_data["snow"]["1h"] if "snow" in weather_data else 0.0,
        weather_data["clouds"]["all"],
        weather_data["wind"].get("speed", 0.0),
        weather_data["wind"].get("deg", 0.0),
        weather_data["wind"].get("gust", 0.0),
    ]

    return out


def main() -> None:
    """Entry point for parsing the current weather data."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", type=str, required=True, help="API key")
    parser.add_argument("--lon", type=float, help="Longitude", default=None)
    parser.add_argument("--lat", type=float, help="Latitude", default=None)
    parser.add_argument(
        "--mode", type=str, help="Response format", default=None
    )
    parser.add_argument(
        "--units",
        type=str,
        help="Units for the response",
        default="metrics",
    )
    parser.add_argument(
        "--lang", type=str, help="Language for the response", default="en"
    )
    parser.add_argument(
        "--out",
        type=str,
        help="Output file directory",
        default=f"{DEFAULT_DATA_DIR}/current.csv",
    )
    args = parser.parse_args()

    weather_data = request_data(
        api_key=args.api_key,
        lat=args.lat,
        lon=args.lon,
        mode=args.mode,
        units=args.units,
        lang=args.lang,
    )
    assert isinstance(weather_data, dict)
    if args.out and Path(args.out).exists():
        out = pd.read_csv(args.out)
    else:
        out = None
    out = process_data(weather_data, out=out)
    out.to_csv(args.out, index=False)


if __name__ == "__main__":
    main()
