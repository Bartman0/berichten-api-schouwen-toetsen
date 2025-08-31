import pytest
import requests
import os
import json
import pandas as pd
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_HOST = os.environ.get("API_HOST")
API_TOKEN = os.environ.get("API_TOKEN")

# --- Configuration ---
# productie URL: https://apigw.idm.diginetwerk.net/api/brp/berichten/v1/berichten
BASE_URL = f"https://{API_HOST}/volgindicaties"  # Assuming a new batch endpoint

# A fixed list of person numbers to be tested against the API.
PERSON_NUMBERS_DEEL_4 = [
    "001",
    "501",
    "502",
    "503",
    "504",
    "505",
    "506",
    "507",
    "509",
    "V02",
]
PERSON_NUMBERS_DEEL_7 = ["005", "150", "501"]

PERSON_NUMBERS_DEEL_9 = ["501", "503", "509", "V12"]


def volgindicaties_put(bsn):
    # 1. Define the API endpoint and the batch payload for the POST request.
    api_url = f"{BASE_URL}/{bsn}"
    payload = {"einddatum": None}
    print(f"Performing PUT to URL: {api_url} with batch payload: {payload}")

    # 2. Make the PUT request to the REST API to initiate the volgindicatie.
    try:
        response = requests.post(api_url, json=payload, timeout=10)
    except requests.exceptions.RequestException as e:
        pytest.fail(f"API request failed. Error: {e}")

    # 3. Assertions on the initial PUT response.
    assert response.status_code == 201, (
        f"Expected status code 201, " f"but got {response.status_code}"
    )

    # 4. Assertions on the contents of the response.
    try:
        response_json = response.json()
        # Assuming a response that separates accepted from rejected items
        begindatum = response_json.get("begindatum", "")
        einddatum = response_json.get("einddatum", "")
        burgerservicenummer = response_json.get("burgerservicenummer", "")

        assert (
            begindatum and einddatum and burgerservicenummer
        ), "Initial response must contain 'begindatum', 'einddatum' and 'burgerservicenummer'."

    except (json.JSONDecodeError, AssertionError) as e:
        pytest.fail(
            f"Could not parse a valid response from the PUT request. Error: {e}"
        )


@pytest.mark.deel_4
def test_deel_4(pl_lookup):
    """
    Tests person list 4
    """
    print(pl_lookup)


@pytest.mark.deel_7
def test_deel_7():
    """
    Tests person list 7
    """


@pytest.mark.deel_9
def test_deel_9():
    """
    Tests person list 9
    """


def main():
    print("hello from schouwen-toetsen!")
    print("run tests through pytest")


if __name__ == "__main__":
    main()
