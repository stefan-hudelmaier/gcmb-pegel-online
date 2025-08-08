import logging
import requests
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ApiClient:
    """
    Client for the Pegel Online API.
    Handles fetching data from the API and parsing the response.
    """
    
    def __init__(self, base_url: str = "https://www.pegelonline.wsv.de/webservices/rest-api/v2"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the Pegel Online API
        """
        self.base_url = base_url
        logger.debug(f"Initialized ApiClient with base URL: {base_url}")
    
    def get_stations(self, include_timeseries: bool = True, include_current_measurement: bool = True) -> List[Dict[str, Any]]:
        """
        Get all stations from the Pegel Online API.
        
        Args:
            include_timeseries: Whether to include timeseries data
            include_current_measurement: Whether to include current measurement data
            
        Returns:
            List of station data
            
        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}/stations.json"
        params = {
            "includeTimeseries": str(include_timeseries).lower(),
            "includeCurrentMeasurement": str(include_current_measurement).lower()
        }
        
        logger.debug(f"Fetching stations from {url} with params {params}")
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            stations = response.json()
            logger.debug(f"Fetched {len(stations)} stations")
            return stations
        except requests.RequestException as e:
            logger.error(f"Error fetching stations: {e}")
            raise
    
    @staticmethod
    def extract_measurement_data(stations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract measurement data from stations.
        
        Args:
            stations: List of station data from the API
            
        Returns:
            List of measurement data with the following structure:
            {
                "water_shortname": str,
                "water_longname": str,
                "station_shortname": str,
                "station_longname": str,
                "latitude": float,
                "longitude": float,
                "measurement_value": float,
                "state_mnw_mhw": str,
                "state_nsw_hsw": str
            }
        """
        measurements = []
        
        for station in stations:
            # Skip stations without water information
            if "water" not in station:
                logger.debug(f"Station {station.get('shortname', 'unknown')} has no water information, skipping")
                continue
                
            # Skip stations without timeseries
            if "timeseries" not in station or not station["timeseries"]:
                logger.debug(f"Station {station.get('shortname', 'unknown')} has no timeseries, skipping")
                continue
            
            water_shortname = station["water"]["shortname"]
            water_longname = station["water"]["longname"]
            station_shortname = station["shortname"]
            station_longname = station["longname"]
            latitude = station.get("latitude")
            longitude = station.get("longitude")
            
            for timeseries in station["timeseries"]:

                if timeseries["unit"] != "cm":
                    logger.debug("Skipping time series that is not in cm")
                    continue

                # Skip timeseries without current measurement
                if "currentMeasurement" not in timeseries:
                    logger.debug(f"Timeseries in station {station_shortname} has no current measurement, skipping")
                    continue
                
                current_measurement = timeseries["currentMeasurement"]

                measurement_value = current_measurement.get("value")
                state_mnw_mhw = current_measurement.get("stateMnwMhw")
                state_nsw_hsw = current_measurement.get("stateNswHsw")
                
                measurements.append({
                    "water_shortname": water_shortname,
                    "water_longname": water_longname,
                    "station_shortname": station_shortname,
                    "station_longname": station_longname,
                    "latitude": latitude,
                    "longitude": longitude,
                    "measurement_value": measurement_value,
                    "state_mnw_mhw": state_mnw_mhw,
                    "state_nsw_hsw": state_nsw_hsw
                })
        
        logger.debug(f"Extracted {len(measurements)} measurements")
        return measurements