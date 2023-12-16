"""Constants for the project."""
from __future__ import annotations

from pathlib import Path
from typing import List

BASE_OPENWEATHER_URL: str = "https://api.openweathermap.org/data/2.5/weather?"
BASE_OPENMETEO_URL: str = "https://archive-api.open-meteo.com/v1/archive"
DEFAULT_DATA_DIR: str = str((Path(__file__).parents[1] / "data").resolve())
DEFAULT_LATITUDE: float = 41.8781
DEFAULT_LONGITUDE: float = -87.6298
SCHEMA: List[str] = [
    "timestamp",
    "longitude",
    "latitude",
    "temperature",  # Temperature, in celcius
    "apparent_temperature",  # Apparent Temperature, in celcius
    "pressure",  # Sea level pressure, in hPa
    "humidity",  # Humidity, in %
    "rain",  # Rain volume for the last hour, in mm
    "snow",  # Snow volume for the last hour, in mm
    "clouds",  # Cloudiness, in %
    "wind_speed",  # Wind speed, in m/s
    "wind_deg",  # Wind direction, in degrees (meteorological)
    "wind_gust",  # Wind gust, in m/s
]
