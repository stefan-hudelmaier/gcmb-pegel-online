#!/usr/bin/env python3
from dotenv import load_dotenv

from utils import sanitize_topic

load_dotenv()

import os
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any

from api_client import ApiClient

# Environment variables
GCMB_ORG = os.environ.get('GCMB_ORG', 'rivers')
GCMB_PROJECT = os.environ.get('GCMB_PROJECT', 'pegel-online')
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

# Base directory for GCMB README files
GCMB_DIR = Path("gcmb")


def ensure_directory(path: Path):
    """
    Ensure that a directory exists.
    
    Args:
        path: Path to the directory
    """
    if not path.exists():
        path.mkdir(parents=True)
        logger.debug(f"Created directory: {path}")


def generate_main_readme(measurements: List[Dict[str, Any]]):
    """
    Generate the main README file for the base topic.
    
    Args:
        measurements: List of measurement data
    """
    # Get unique rivers
    rivers = {}
    for measurement in measurements:
        water_shortname = measurement["water_shortname"]
        water_longname = measurement["water_longname"]
        rivers[water_shortname] = water_longname
    
    # Sort rivers by longname
    sorted_rivers = sorted(rivers.items(), key=lambda x: x[1])
    
    # Generate README content
    content = "# Pegel Online\n\n"

    content += "Live water levels of German waterways.\n\n"

    content += "## Origin of data\n\n"
    content += "This data is originally provided by the [Wasserstrassen- und Schifffahrtsverwaltung des Bundes](https://www.gdws.wsv.bund.de/).\n"
    content += "It is published under the license: [DL-DE->Zero-2.0](https://www.govdata.de/dl-de/zero-2-0)\n\n"

    content += "## List of rivers/waters\n\n"
    
    for shortname, longname in sorted_rivers:
        content += f"* [{longname}](./{sanitize_topic(shortname)})\n"
    
    # Write README file
    readme_path = GCMB_DIR / "README.md"
    with open(readme_path, "w") as f:
        f.write(content)
    
    logger.info(f"Generated main README at {readme_path}")


def generate_river_readmes(measurements: List[Dict[str, Any]]):
    """
    Generate README files for each river.
    
    Args:
        measurements: List of measurement data
    """
    # Group measurements by river
    rivers = {}
    for measurement in measurements:
        water_shortname = measurement["water_shortname"]
        if water_shortname not in rivers:
            rivers[water_shortname] = {
                "longname": measurement["water_longname"],
                "stations": {}
            }
        
        station_shortname = measurement["station_shortname"]
        rivers[water_shortname]["stations"][station_shortname] = {
            "longname": measurement["station_longname"],
            "measurement_value": measurement["measurement_value"]
        }
    
    # Generate README for each river
    for water_shortname, river_data in rivers.items():
        water_longname = river_data["longname"]
        
        # Create directory for river
        river_dir = GCMB_DIR / sanitize_topic(water_shortname)
        ensure_directory(river_dir)
        
        # Sort stations by longname
        sorted_stations = sorted(
            river_data["stations"].items(),
            key=lambda x: x[1]["longname"]
        )
        
        # Generate README content
        content = f"# {water_longname}\n\n"
        content += "List of measuring points:\n\n"
        
        for station_shortname, station_data in sorted_stations:
            station_longname = station_data["longname"]
            topic = sanitize_topic(f"{GCMB_ORG}/{GCMB_PROJECT}/{water_shortname}/{station_shortname}/measurementValue")
            content += f"* [{station_longname}](./{sanitize_topic(station_shortname)}): <Value topic=\"{topic}\"/> cm\n"
        
        # Write README file
        readme_path = river_dir / "README.md"
        with open(readme_path, "w") as f:
            f.write(content)
        
        logger.info(f"Generated river README at {readme_path}")


def generate_station_readmes(measurements: List[Dict[str, Any]]):
    """
    Generate README files for each station.
    
    Args:
        measurements: List of measurement data
    """
    # Group measurements by station
    stations = {}
    for measurement in measurements:
        water_shortname = measurement["water_shortname"]
        water_longname = measurement["water_longname"]
        station_shortname = measurement["station_shortname"]
        
        key = (water_shortname, station_shortname)
        if key not in stations:
            stations[key] = {
                "water_longname": water_longname,
                "station_longname": measurement["station_longname"],
                "latitude": measurement["latitude"],
                "longitude": measurement["longitude"]
            }
    
    # Generate README for each station
    for (water_shortname, station_shortname), station_data in stations.items():
        water_longname = station_data["water_longname"]
        latitude = station_data["latitude"]
        longitude = station_data["longitude"]
        
        # Create directory for station
        station_dir = GCMB_DIR / sanitize_topic(water_shortname) / sanitize_topic(station_shortname)
        ensure_directory(station_dir)
        
        # Generate README content
        content = f"# {water_longname} - {station_shortname}\n\n"

        station_topic = sanitize_topic(f"{GCMB_ORG}/{GCMB_PROJECT}/{water_shortname}/{station_shortname}")
        
        content += "## Current Measurement\n\n"
        content += f"Current measurement: <Value topic=\"{station_topic}/measurementValue\"/> cm\n\n"
        
        content += "## Time Series\n\n"
        content += f"<TimeSeries topic=\"{station_topic}/measurementValue\" period=\"week\" />\n\n"
        
        content += "## Location\n\n"
        content += "<WorldMap>\n"
        content += f"  <Marker lat=\"{latitude}\" lon=\"{longitude}\" labelTopic=\"{station_topic}/measurementValue\" />\n"
        content += "</WorldMap>\n"
        
        # Write README file
        readme_path = station_dir / "README.md"
        with open(readme_path, "w") as f:
            f.write(content)
        
        logger.info(f"Generated station README at {readme_path}")


def main():
    """
    Main entry point for generating GCMB README files.
    """
    logger.info("Starting generation of GCMB README files")
    
    try:
        # Create API client
        api_client = ApiClient()
        
        # Fetch stations from API
        stations = api_client.get_stations()
        
        # Extract measurement data
        measurements = api_client.extract_measurement_data(stations)
        
        # Ensure base directory exists
        ensure_directory(GCMB_DIR)
        
        # Generate README files
        generate_main_readme(measurements)
        generate_river_readmes(measurements)
        generate_station_readmes(measurements)
        
        logger.info("Successfully generated all GCMB README files")
    except Exception as e:
        logger.error(f"Error generating GCMB README files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()