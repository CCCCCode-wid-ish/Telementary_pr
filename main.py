from flask import Flask
import os
import json
import unittest
import datetime

app = Flask('')

# --- Data Loading and Processing Logic ---

# Use the open function to read the three json files
with open("./data-1.json", "r", encoding="utf-8") as f:
    jsonData1 = json.load(f)

with open("./data-2.json", "r", encoding="utf-8") as f:
    jsonData2 = json.load(f)

with open("./data-result.json", "r", encoding="utf-8") as f:
    jsonExpectedResult = json.load(f)


# Convert json data from format 1 to the expected format
def convertFromFormat1(jsonObject):
    locationParts = jsonObject["location"].split("/")
    result = {
        'deviceID': jsonObject['deviceID'],
        'deviceType': jsonObject['deviceType'],
        'timestamp': jsonObject['timestamp'],
        'location': {
            'country': locationParts[0],
            'city': locationParts[1],
            'area': locationParts[2],
            'factory': locationParts[3],
            'section': locationParts[4]
        },
        'data': {
            'status': jsonObject['operationStatus'],
            'temperature': jsonObject['temp']
        }
    }
    return result


# Convert json data from format 2 to the expected format
def convertFromFormat2(jsonObject):
    data = datetime.datetime.strptime(
        jsonObject['timestamp'],
        '%Y-%m-%dT%H:%M:%S.%fZ'
    )
    timestamp = round(
        (data - datetime.datetime(1970, 1, 1)).total_seconds() * 1000
    )
    result = {
        'deviceID': jsonObject['device']['id'],
        'deviceType': jsonObject['device']['type'],
        'timestamp': timestamp,
        'location': {
            'country': jsonObject['country'],
            'city': jsonObject['city'],
            'area': jsonObject['area'],
            'factory': jsonObject['factory'],
            'section': jsonObject['section']
        },
        'data': jsonObject['data']
    }
    return result


def main(jsonObject):
    if jsonObject.get('device') is None:
        return convertFromFormat1(jsonObject)
    else:
        return convertFromFormat2(jsonObject)


# --- Upgraded Web Route Definition ---
# Placed here so it can cleanly read jsonData1 and invoke main()
@app.route('/')
def home():
    try:
        sample_output = main(jsonData1)
        return {
            "status": "Telementary Project is Live!",
            "test_environment": "Railway Cloud",
            "sample_converted_data": sample_output
        }
    except Exception as e:
        return f"Server is live, but data processing encountered an error: {str(e)}"


# --- Unit Test Assertions ---
class TestSolution(unittest.TestCase):
    def test_sanity(self):
        result = json.loads(json.dumps(jsonExpectedResult))
        self.assertEqual(result, jsonExpectedResult)

    def test_dataType1(self):
        result = main(jsonData1)
        self.assertEqual(result, jsonExpectedResult, "Converting from Type 1 failed")

    def test_dataType2(self):
        result = main(jsonData2)
        self.assertEqual(result, jsonExpectedResult, "Converting from Type 2 failed")


# --- Production Execution Entrypoint ---
if __name__ == '__main__':
    print("Running telemetry data format tests...")
    
    # 1. Run the test suite programmatically inside the logs
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSolution)
    runner = unittest.TextTestRunner()
    test_result = runner.run(suite)
    
    # 2. Spin up the server loop on the primary thread
    print("Tests completed. Starting web app deployment...")
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)