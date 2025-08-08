from dotenv import load_dotenv
load_dotenv()

import os
import logging
import sys
import time
from typing import Dict, Any, Optional
from gcmb_publisher import MqttPublisher
from api_client import ApiClient

# Environment variables
GCMB_ORG = os.environ.get('GCMB_ORG', 'rivers')
GCMB_PROJECT = os.environ.get('GCMB_PROJECT', 'pegel-online')
FETCH_INTERVAL = int(os.environ.get('FETCH_INTERVAL', '300'))  # Default: 5 minutes
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Configure logging
print(f"Using log level: {LOG_LEVEL}")
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Adapter:
    """
    Adapter for fetching data from Pegel Online API and publishing to MQTT.
    """

    def __init__(self, gcmb_org: str, gcmb_project: str, fetch_interval: int = 300):
        """
        Initialize the adapter.

        Args:
            gcmb_org: GCMB organization
            gcmb_project: GCMB project
            fetch_interval: Interval between fetches in seconds
        """
        self.gcmb_org = gcmb_org
        self.gcmb_project = gcmb_project
        self.fetch_interval = fetch_interval
        self.base_topic = f"{gcmb_org}/{gcmb_project}"
        self.api_client = ApiClient()
        self.mqtt_publisher = MqttPublisher(enable_watchdog=True)

        logger.info(f"Initialized Adapter with base topic: {self.base_topic}")
        logger.info(f"Fetch interval: {self.fetch_interval} seconds")

    def run(self):
        """
        Run the adapter's main loop.
        Fetches data from the API and publishes it to MQTT.
        """
        logger.info("Starting adapter main loop")

        while True:
            try:
                self._fetch_and_publish()
            except Exception as e:
                logger.error(f"Error in fetch and publish cycle: {e}")

            logger.debug(f"Sleeping for {self.fetch_interval} seconds")
            time.sleep(self.fetch_interval)

    def _fetch_and_publish(self):
        """
        Fetch data from the API and publish it to MQTT.
        """
        logger.debug("Fetching data from Pegel Online API")

        try:
            # Fetch stations from API
            stations = self.api_client.get_stations()

            # Extract measurement data
            measurements = self.api_client.extract_measurement_data(stations)

            # Publish measurements
            self._publish_measurements(measurements)

            logger.info(f"Successfully published {len(measurements)} measurements")
        except Exception as e:
            logger.error(f"Error fetching or publishing data: {e}")
            raise

    def _publish_measurements(self, measurements):
        """
        Publish measurements to MQTT.

        Args:
            measurements: List of measurement data
        """
        for measurement in measurements:
            water_shortname = measurement["water_shortname"]
            station_shortname = measurement["station_shortname"]

            # Base topic for this measurement
            measurement_base_topic = f"{self.base_topic}/{water_shortname}/{station_shortname}"

            # Publish measurement value
            if measurement["measurement_value"] is not None:
                self.mqtt_publisher.send_msg(
                    str(measurement["measurement_value"]),
                    f"{measurement_base_topic}/measurementValue",
                    retain=True
                )

            # Publish state_mnw_mhw if available
            if measurement["state_mnw_mhw"] is not None:
                self.mqtt_publisher.send_msg(
                    measurement["state_mnw_mhw"],
                    f"{measurement_base_topic}/stateMnwMhw",
                    retain=True
                )

            # Publish state_nsw_hsw if available
            if measurement["state_nsw_hsw"] is not None:
                self.mqtt_publisher.send_msg(
                    measurement["state_nsw_hsw"],
                    f"{measurement_base_topic}/stateNswHsw",
                    retain=True
                )


def main():
    """
    Main entry point for the adapter.
    """
    adapter = Adapter(
        gcmb_org=GCMB_ORG,
        gcmb_project=GCMB_PROJECT,
        fetch_interval=FETCH_INTERVAL
    )
    adapter.run()


if __name__ == '__main__':
    main()
