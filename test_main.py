import pytest
from unittest.mock import MagicMock, patch
import json
from pathlib import Path

from main import Adapter
from utils.mock_mqtt_publisher import MockMqttPublisher


@pytest.fixture
def sample_stations():
    """
    Fixture providing sample station data from the API.
    """
    return [
        {
            "uuid": "b475386c-30cc-453a-b3b7-1d17ace13595",
            "number": "48300105",
            "shortname": "CELLE",
            "longname": "CELLE",
            "km": 1.74,
            "agency": "VERDEN",
            "longitude": 10.062164093638698,
            "latitude": 52.62270553213209,
            "water": {
                "shortname": "ALLER",
                "longname": "ALLER"
            },
            "timeseries": [
                {
                    "shortname": "W",
                    "longname": "WASSERSTAND ROHDATEN",
                    "unit": "cm",
                    "equidistance": 15,
                    "currentMeasurement": {
                        "timestamp": "2025-08-08T16:15:00+02:00",
                        "value": 115.0,
                        "stateMnwMhw": "low",
                        "stateNswHsw": "normal"
                    },
                    "gaugeZero": {
                        "unit": "m. ü. NN",
                        "value": 31.82,
                        "validFrom": "1936-11-01"
                    }
                }
            ]
        },
        {
            "uuid": "8b4f9f7c-3376-4dd8-95c1-de55b1be4dfd",
            "number": "48700103",
            "shortname": "MARKLENDORF",
            "longname": "MARKLENDORF",
            "km": 38.47,
            "agency": "VERDEN",
            "longitude": 9.70345575731809,
            "latitude": 52.68275727270215,
            "water": {
                "shortname": "ALLER",
                "longname": "ALLER"
            },
            "timeseries": [
                {
                    "shortname": "W",
                    "longname": "WASSERSTAND ROHDATEN",
                    "unit": "cm",
                    "equidistance": 15,
                    "currentMeasurement": {
                        "timestamp": "2025-08-08T16:15:00+02:00",
                        "value": 102.0,
                        "stateMnwMhw": "low",
                        "stateNswHsw": "normal"
                    },
                    "gaugeZero": {
                        "unit": "m. ü. NN",
                        "value": 23.01,
                        "validFrom": "1950-11-01"
                    }
                }
            ]
        }
    ]


@pytest.fixture
def sample_measurements():
    """
    Fixture providing sample measurement data extracted from stations.
    """
    return [
        {
            "water_shortname": "ALLER",
            "water_longname": "ALLER",
            "station_shortname": "CELLE",
            "station_longname": "CELLE",
            "latitude": 52.62270553213209,
            "longitude": 10.062164093638698,
            "measurement_value": 115.0,
            "state_mnw_mhw": "low",
            "state_nsw_hsw": "normal"
        },
        {
            "water_shortname": "ALLER",
            "water_longname": "ALLER",
            "station_shortname": "MARKLENDORF",
            "station_longname": "MARKLENDORF",
            "latitude": 52.68275727270215,
            "longitude": 9.70345575731809,
            "measurement_value": 102.0,
            "state_mnw_mhw": "low",
            "state_nsw_hsw": "normal"
        }
    ]


def test_adapter_initialization():
    """
    Test that the adapter initializes correctly.
    """
    # Create adapter with test values
    adapter = Adapter(
        gcmb_org="test-org",
        gcmb_project="test-project",
        fetch_interval=60
    )
    
    # Check that the adapter has the correct properties
    assert adapter.gcmb_org == "test-org"
    assert adapter.gcmb_project == "test-project"
    assert adapter.fetch_interval == 60
    assert adapter.base_topic == "test-org/test-project"


def test_publish_measurements(sample_measurements):
    """
    Test that measurements are published to the correct MQTT topics.
    """
    # Create adapter with mock MQTT publisher
    mock_publisher = MockMqttPublisher()
    
    adapter = Adapter(
        gcmb_org="rivers",
        gcmb_project="pegel-online",
        fetch_interval=60
    )
    adapter.mqtt_publisher = mock_publisher
    
    # Call the method to publish measurements
    adapter._publish_measurements(sample_measurements)
    
    # Check that the correct messages were published
    messages = mock_publisher.get_all_messages()
    
    # Should have 6 messages (3 per measurement)
    assert len(messages) == 6
    
    # Check messages for CELLE
    celle_value = mock_publisher.get_payloads_by_topic("rivers/pegel-online/ALLER/CELLE/measurementValue")
    assert celle_value == ["115.0"]
    
    celle_mnw_mhw = mock_publisher.get_payloads_by_topic("rivers/pegel-online/ALLER/CELLE/stateMnwMhw")
    assert celle_mnw_mhw == ["low"]
    
    celle_nsw_hsw = mock_publisher.get_payloads_by_topic("rivers/pegel-online/ALLER/CELLE/stateNswHsw")
    assert celle_nsw_hsw == ["normal"]
    
    # Check messages for MARKLENDORF
    marklendorf_value = mock_publisher.get_payloads_by_topic("rivers/pegel-online/ALLER/MARKLENDORF/measurementValue")
    assert marklendorf_value == ["102.0"]
    
    marklendorf_mnw_mhw = mock_publisher.get_payloads_by_topic("rivers/pegel-online/ALLER/MARKLENDORF/stateMnwMhw")
    assert marklendorf_mnw_mhw == ["low"]
    
    marklendorf_nsw_hsw = mock_publisher.get_payloads_by_topic("rivers/pegel-online/ALLER/MARKLENDORF/stateNswHsw")
    assert marklendorf_nsw_hsw == ["normal"]


@patch('main.ApiClient')
def test_fetch_and_publish(mock_api_client_class, sample_stations, sample_measurements):
    """
    Test the fetch and publish cycle.
    """
    # Create mock API client
    mock_api_client = MagicMock()
    mock_api_client.get_stations.return_value = sample_stations
    mock_api_client.extract_measurement_data.return_value = sample_measurements
    
    # Make the mock API client class return our mock instance
    mock_api_client_class.return_value = mock_api_client
    
    # Create adapter with mock MQTT publisher
    mock_publisher = MockMqttPublisher()
    
    adapter = Adapter(
        gcmb_org="rivers",
        gcmb_project="pegel-online",
        fetch_interval=60
    )
    adapter.mqtt_publisher = mock_publisher
    adapter.api_client = mock_api_client
    
    # Call the method to fetch and publish
    adapter._fetch_and_publish()
    
    # Check that the API client methods were called
    mock_api_client.get_stations.assert_called_once()
    mock_api_client.extract_measurement_data.assert_called_once_with(sample_stations)
    
    # Check that the correct messages were published
    messages = mock_publisher.get_all_messages()
    
    # Should have 6 messages (3 per measurement)
    assert len(messages) == 6
    
    # Check that all expected topics were published to
    topics = mock_publisher.get_all_topics()
    expected_topics = [
        "rivers/pegel-online/ALLER/CELLE/measurementValue",
        "rivers/pegel-online/ALLER/CELLE/stateMnwMhw",
        "rivers/pegel-online/ALLER/CELLE/stateNswHsw",
        "rivers/pegel-online/ALLER/MARKLENDORF/measurementValue",
        "rivers/pegel-online/ALLER/MARKLENDORF/stateMnwMhw",
        "rivers/pegel-online/ALLER/MARKLENDORF/stateNswHsw"
    ]
    
    for topic in expected_topics:
        assert topic in topics


def test_handle_missing_data():
    """
    Test that the adapter handles missing data gracefully.
    """
    # Create measurements with missing data
    measurements = [
        {
            "water_shortname": "ALLER",
            "water_longname": "ALLER",
            "station_shortname": "CELLE",
            "station_longname": "CELLE",
            "latitude": 52.62270553213209,
            "longitude": 10.062164093638698,
            "measurement_value": None,  # Missing value
            "state_mnw_mhw": "low",
            "state_nsw_hsw": None  # Missing value
        }
    ]
    
    # Create adapter with mock MQTT publisher
    mock_publisher = MockMqttPublisher()
    
    adapter = Adapter(
        gcmb_org="rivers",
        gcmb_project="pegel-online",
        fetch_interval=60
    )
    adapter.mqtt_publisher = mock_publisher
    
    # Call the method to publish measurements
    adapter._publish_measurements(measurements)
    
    # Check that only the available data was published
    messages = mock_publisher.get_all_messages()
    
    # Should have 1 message (only stateMnwMhw is available)
    assert len(messages) == 1
    
    # Check that the message was published to the correct topic
    topics = mock_publisher.get_all_topics()
    assert "rivers/pegel-online/ALLER/CELLE/stateMnwMhw" in topics
    assert "rivers/pegel-online/ALLER/CELLE/measurementValue" not in topics
    assert "rivers/pegel-online/ALLER/CELLE/stateNswHsw" not in topics