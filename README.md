# Weather Data Pipeline and Visualization Project

## Project Overview

This project establishes a real-time data pipeline to fetch weather data from OpenWeatherMap, stream it through Google Cloud Pub/Sub, store it in Google BigQuery, and visualize it using Looker Studio. It leverages various Google Cloud Platform (GCP) services to create a comprehensive solution for weather data analysis.

## Components

- **OpenWeatherMap API**: Source of real-time weather data.
- **Google Cloud Function**: Fetches weather data and publishes it to a Pub/Sub topic.
- **Google Cloud Pub/Sub**: Messaging service for weather data.
- **Google Cloud Dataflow**: Streams data from Pub/Sub to BigQuery.
- **Google BigQuery**: Data warehouse for storing weather data.
- **Looker Studio**: Tool for visualizing data from BigQuery.

## Setup and Configuration

### 1. OpenWeatherMap API
- Obtain an API key from OpenWeatherMap.
- API Endpoint: `http://api.openweathermap.org/data/2.5/weather`

### 2. Google Cloud Function
- Implemented in Python.
- Retrieves data from OpenWeatherMap.
- Transforms and publishes data to a Pub/Sub topic.

### 3. Google Cloud Pub/Sub
- Create a topic for receiving weather data.
- Configure permissions for Cloud Function publishing.

### 4. Google Cloud Dataflow
- Utilize "Pub/Sub Subscription to BigQuery" template.
- Configure to read from Pub/Sub topic and write to BigQuery table.

### 5. Google BigQuery
- Create a dataset and table for weather data.
- Schema aligned with transformed data structure.

#### BigQuery Schema
timestamp: TIMESTAMP,
latitude: FLOAT,
longitude: FLOAT,
temperature: FLOAT,
humidity: INTEGER,
pressure: INTEGER,
wind_speed: FLOAT,
wind_deg: INTEGER,
clouds: INTEGER,
visibility: INTEGER,
weather_main: STRING,
weather_description: STRING,
temp_min: FLOAT,
temp_max: FLOAT,
feels_like: FLOAT,
sea_level: INTEGER,
grnd_level: INTEGER,
sunrise: TIMESTAMP,
sunset: TIMESTAMP


### 6. Looker Studio
- Connect to BigQuery dataset.
- Create and view reports for data analysis.

## Usage Instructions

1. Deploy the Cloud Function with appropriate environment variables.
2. Ensure Dataflow job is active for data streaming to BigQuery.
3. Trigger Cloud Function for regular data publishing.
4. Utilize Looker Studio for data visualization and reporting.

## Monitoring and Maintenance

- Monitor Cloud Function and Dataflow job for operational issues.
- Verify data integrity and completeness in BigQuery.
- Update Cloud Function for any changes in API response format.

