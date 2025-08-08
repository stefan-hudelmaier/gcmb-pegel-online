# pegel-online Adapter

This project is a Python-based adapter that fetches water level data from the Pegel Online API and publishes it to MQTT for use with GCMB.

## Features

* Fetches water level data from the [Pegel Online API](https://www.pegelonline.wsv.de/)
* Publishes measurement data to MQTT topics
* Generates topic-specific README files for GCMB
* Runs on a configurable interval (default: every 5 minutes)

## Setup

1. Copy `.env.template` to `.env` and configure your environment variables:
   ```
   cp .env.template .env
   ```
2. Edit the `.env` file to set your MQTT credentials and other configuration options.
3. Install dependencies:
   ```
   ~/.local/bin/uv pip install -e .
   ```

## Usage

* Run the adapter:
  ```
  just run
  ```
* Generate GCMB README files:
  ```
  python generate_gcmb_readmes.py
  ```
* Run tests:
  ```
  just tests
  ```

## Data Structure

The adapter publishes data to the following MQTT topics:

* `{GCMB_ORG}/{GCMB_PROJECT}/{WATER_SHORT_NAME}/{MEASUREMENT_POINT_SHORT_NAME}/measurementValue`: Water level measurement value in cm
* `{GCMB_ORG}/{GCMB_PROJECT}/{WATER_SHORT_NAME}/{MEASUREMENT_POINT_SHORT_NAME}/stateMnwMhw`: State of the water level (e.g., "low", "normal", "high")
* `{GCMB_ORG}/{GCMB_PROJECT}/{WATER_SHORT_NAME}/{MEASUREMENT_POINT_SHORT_NAME}/stateNswHsw`: State of the water level (e.g., "normal")

## License

This project is provided under the MIT License.
