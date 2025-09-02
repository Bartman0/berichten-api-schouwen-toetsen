import pytest
import requests
import os
import logging
import json
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
logger = logging.getLogger()

API_BASE_URL = os.environ.get("API_BASE_URL")
API_TOKEN = os.environ.get("API_TOKEN")
API_URL = f"{API_BASE_URL}/volgindicaties"  # Assuming a new batch endpoint

EINDDATUM = "2025-12-31"

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


def volgindicaties_put(bsn, einddatum, status_code_ok):
    api_url = f"{API_URL}/{bsn}"
    payload = {"einddatum": einddatum}
    request_put(api_url, payload, status_code_ok)


def request_put(api_url, payload, status_code_ok):
    logger.info(f"Performing PUT to URL: {api_url} with payload: {payload}")

    try:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Accept": "application/json, application/hal+json",
            "Content-Type": "application/json",
        }
        logger.debug(f"Headers: {headers}")
        response = requests.put(api_url, json=payload, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        pytest.fail(f"API request failed. Error: {e}")

    assert response.status_code == status_code_ok, (
        f"Expected status code {status_code_ok}, " f"but got {response.status_code}"
    )

    try:
        response_json = response.json()
        einddatum = response_json.get("einddatum")

        assert einddatum, "Response must contain 'einddatum'."
    except (json.JSONDecodeError, AssertionError) as e:
        pytest.fail(
            f"Could not parse a valid response from the PUT request. Error: {e}"
        )


@pytest.mark.deel_4
def test_deel_4(pl_lookup):
    for pl_nummer in PERSON_NUMBERS_DEEL_4:
        logger.debug(f"[{pl_nummer}]")
        bsn = pl_lookup[pl_nummer]
        volgindicaties_put(bsn, einddatum=EINDDATUM, status_code_ok=201)


@pytest.mark.deel_7
def test_deel_7(pl_lookup):
    for pl_nummer in PERSON_NUMBERS_DEEL_7:
        logger.debug(f"[{pl_nummer}]")
        bsn = pl_lookup[pl_nummer]
        volgindicaties_put(bsn, einddatum=EINDDATUM, status_code_ok=201)


@pytest.mark.deel_9
def test_deel_9(pl_lookup):
    for pl_nummer in PERSON_NUMBERS_DEEL_9:
        logger.debug(f"[{pl_nummer}]")
        bsn = pl_lookup[pl_nummer]
        volgindicaties_put(bsn, einddatum=EINDDATUM, status_code_ok=201)


def main():
    print("hello from schouwen-toetsen!")
    print("run tests through pytest")


if __name__ == "__main__":
    main()
