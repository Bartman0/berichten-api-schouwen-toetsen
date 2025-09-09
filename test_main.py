import pytest
import requests
import os
import logging
import json
from dotenv import load_dotenv, find_dotenv
from datetime import date, timedelta


load_dotenv(find_dotenv())
logger = logging.getLogger()

API_BASE_URL = os.environ.get("API_BASE_URL")
API_TOKEN = os.environ.get("API_TOKEN")
API_URL_VOLGINDICATIES = (
    f"{API_BASE_URL}/volgindicaties"  # Assuming a new batch endpoint
)
API_URL_WIJZIGINGEN = f"{API_BASE_URL}/wijzigingen"  # Assuming a new batch endpoint
API_URL_NIEUWE_INGEZETENEN = (
    f"{API_BASE_URL}/nieuwe-ingezetenen"  # Assuming a new batch endpoint
)

EINDDATUM = "2025-12-31"

# A fixed list of person numbers to be tested against the API.
PERSON_NUMBERS_DEEL_4_PLAATSEN = ["001", "V02"]

PERSON_NUMBERS_DEEL_4_VERWIJDER = [
    "501",
    "502",
    "503",
    "504",
    "505",
    "506",
    "507",
    "509",
]

PERSON_NUMBERS_DEEL_4_VERWACHT = ["V02"]

PERSON_NUMBERS_DEEL_7_PLAATSEN = ["005"]

PERSON_NUMBERS_DEEL_7_VERWIJDER = ["150", "501"]

PERSON_NUMBERS_DEEL_7_VERWACHT = ["005", "V02"]

PERSON_NUMBERS_DEEL_9_PLAATSEN = ["501", "509"]

PERSON_NUMBERS_DEEL_9_VERWIJDER = ["501", "509"]


def volgindicaties_put(bsn, einddatum, status_code_ok):
    api_url = f"{API_URL_VOLGINDICATIES}/{bsn}"
    payload = {"einddatum": einddatum}
    request_volgindicatie_put(api_url, payload, status_code_ok)


def wijzigingen_get(vanaf, burgerservicenummers_verwacht, status_code_ok):
    api_url = f"{API_URL_WIJZIGINGEN}"
    parameters = {"vanaf": vanaf}
    burgerservicenummers = set(
        request_wijzigingen_get(api_url, parameters, status_code_ok)
    )
    assert (
        burgerservicenummers & burgerservicenummers_verwacht
        == burgerservicenummers_verwacht
    )


def today():
    return (date.today()).strftime("%Y-%m-%d")


def yesterday():
    return (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")


def request_wijzigingen_get(api_url, parameters, status_code_ok):
    logger.info(f"Performing GET on URL: {api_url} with parameters: {parameters}")

    try:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Accept": "application/json, application/hal+json",
            "Content-Type": "application/json",
        }
        logger.debug(f"Headers: {headers}")
        response = requests.get(api_url, params=parameters, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        pytest.fail(f"API request failed. Error: {e}")

    # relax the test for the status code by looking only at the major value
    assert response.status_code // 100 == status_code_ok // 100, (
        f"Expected status code {status_code_ok}, " f"but got {response.status_code}"
    )

    try:
        results = response.json()
        burgerservicenummers = response_json.get("burgerservicenummers")

        assert burgerservicenummers, "Response must contain 'burgerservicenummers'."
        return burgerservicenummers
    except (json.JSONDecodeError, AssertionError) as e:
        pytest.fail(
            f"Could not parse a valid response from the GET request. Error: {e}"
        )


def request_volgindicatie_put(api_url, payload, status_code_ok):
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

    # relax the test for the status code by looking only at the major value
    assert response.status_code // 100 == status_code_ok // 100, (
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


def volgindicaties_create_plnummer(pl_lookup, pl_nummer):
    logger.debug(f"[{pl_nummer}]")
    bsn = pl_lookup[pl_nummer]
    volgindicaties_put(bsn, einddatum=EINDDATUM, status_code_ok=201)


def volgindicaties_delete_plnummer(pl_lookup, pl_nummer):
    logger.debug(f"[{pl_nummer}]")
    bsn = pl_lookup[pl_nummer]
    volgindicaties_put(bsn, einddatum=yesterday(), status_code_ok=200)


@pytest.mark.deel_4
def test_deel_4(pl_lookup):
    for pl_nummer in PERSON_NUMBERS_DEEL_4:
        volgindicaties_create_plnummer(pl_lookup, pl_nummer)


@pytest.mark.deel_4_verwijder
def test_deel_4_verwijder(pl_lookup):
    for pl_nummer in PERSON_NUMBERS_DEEL_4:
        volgindicaties_delete_plnummer(pl_lookup, pl_nummer)


@pytest.mark.deel_4_verwacht
def test_deel_4_verwacht(pl_lookup):
    burgerservicenummers = [
        pl_lookup[pl_nummer] for pl_nummer in PERSON_NUMBERS_DEEL_4_VERWACHT
    ]
    wijzigingen_get(today, burgerservicenummers, status_code_ok=200)


@pytest.mark.deel_7
def test_deel_7(pl_lookup):
    for pl_nummer in PERSON_NUMBERS_DEEL_7:
        volgindicaties_create_plnummer(pl_lookup, pl_nummer)


@pytest.mark.deel_7_verwijder
def test_deel_7_verwijder(pl_lookup):
    for pl_nummer in PERSON_NUMBERS_DEEL_7:
        volgindicaties_delete_plnummer(pl_lookup, pl_nummer)


@pytest.mark.deel_7_verwacht
def test_deel_7_verwacht(pl_lookup):
    burgerservicenummers = [
        pl_lookup[pl_nummer] for pl_nummer in PERSON_NUMBERS_DEEL_7_VERWACHT
    ]
    wijzigingen_get(today, burgerservicenummers, status_code_ok=200)


@pytest.mark.deel_9
def test_deel_9(pl_lookup):
    for pl_nummer in PERSON_NUMBERS_DEEL_9:
        volgindicaties_create_plnummer(pl_lookup, pl_nummer)


@pytest.mark.deel_9_verwijder
def test_deel_9_verwijder(pl_lookup):
    for pl_nummer in PERSON_NUMBERS_DEEL_9:
        volgindicaties_delete_plnummer(pl_lookup, pl_nummer)


@pytest.mark.deel_9_verwacht
def test_deel_9_verwacht(pl_lookup):
    burgerservicenummers = [
        pl_lookup[pl_nummer] for pl_nummer in PERSON_NUMBERS_DEEL_9_VERWACHT
    ]
    wijzigingen_get(today, burgerservicenummers, status_code_ok=200)


def main():
    print("hello from schouwen-toetsen!")
    print("run tests through pytest")


if __name__ == "__main__":
    main()
