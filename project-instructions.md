This project shall regularly (every 5 minutes) fetch data from https://www.pegelonline.wsv.de/ and publish data to MQTT broker.

An example for using the pegelonline REST API can be found here.

Getting all cities can be achieved using https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations.json?includeTimeseries=true&includeCurrentMeasurement=true. This is an example response:

```json

[
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
```

The following messages shall be published:

topic: rivers/pegel-online/{WATER_SHORT_NAME}/{MEASUREMENT_POINT_SHORT_NAME}/measurementValue: 102.1
topic: rivers/pegel-online/{WATER_SHORT_NAME}/{MEASUREMENT_POINT_SHORT_NAME}/stateMnwMhw: "low"
topic: rivers/pegel-online/{WATER_SHORT_NAME}/{MEASUREMENT_POINT_SHORT_NAME}/stateNswHsw: "normal"

topic-specific README.md are created:

topic: rivers/pegel-online: Contents:

```markdown
# Pegel Online

List of rivers:

* [WATER_LONG_NAME](./WATER_SHORT_NAME)
...
```

topic rivers/pegel-online/{WATER_SHORT_NAME}: Contents:

```markdown
# {WATER_LONG_NAME}

List of measuring points:

{per measurement point}

* {MEASUREMENT_POINT_LONG_NAME}: <Value topic="rivers/pegel-online/{WATER_SHORT_NAME}/{MEASUREMENT_POINT_SHORT_NAME}/measurementValue"/> cm

```

topic rivers/pegel-online/{WATER_SHORT_NAME}/{MEASUREMENT_POINT_SHORT_NAME}: Contents:

```markdown
# {WATER_LONG_NAME} - {MEASUREMENT_POINT_SHORT_NAME}

## Current Measurement

Current measurement: <Value topic="rivers/pegel-online/{WATER_SHORT_NAME}/{MEASUREMENT_POINT_SHORT_NAME}/measurementValue"/> cm

## Time Series

<TimeSeries topic="rivers/pegel-online/{WATER_SHORT_NAME}/{MEASUREMENT_POINT_SHORT_NAME}/measurementValue" period="week" />

## Location

<WorldMap>
  <Marker lat="{LAT}" lon="{LON}" labelTopic="rivers/pegel-online/{WATER_SHORT_NAME}/{MEASUREMENT_POINT_SHORT_NAME}" />
</WorldMap>
```