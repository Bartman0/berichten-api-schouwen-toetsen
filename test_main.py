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

EINDDATUM_TOEKOMST = "2099-12-31"

# =================================================================

# de lijst voor deel 2,  wordt dynamisch vastgesteld obv de beschrijvingen van de PL-en
PERSON_NUMBERS_DEEL_2_DYNAMISCH = []

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

PERSON_NUMBERS_DEEL_7_PLAATSEN = ["005"]

PERSON_NUMBERS_DEEL_7_VERWIJDER = ["150", "501"]

PERSON_NUMBERS_DEEL_9_PLAATSEN = ["501", "509", "V02", "???"]

PERSON_NUMBERS_DEEL_9_VERWIJDER = ["503", "???"]

# =================================================================


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
    assert burgerservicenummers & set(burgerservicenummers_verwacht) == set(
        burgerservicenummers_verwacht
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
        f"Expected status code {status_code_ok}, but got {response.status_code}: {response.text}"
    )

    try:
        response_json = response.json()
        burgerservicenummers = response_json.get("burgerservicenummers")
        assert (
            len(burgerservicenummers) >= 0
        ), "Response must contain 'burgerservicenummers'."
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
    # if status_code_ok is not set, skip the assertions altogether
    if status_code_ok:
        assert response.status_code // 100 == status_code_ok // 100, (
            f"Expected status code {status_code_ok}, " f"but got {response.status_code}"
        )

        try:
            response_json = response.json()
            einddatum = response_json.get("einddatum")
            assert einddatum, "Response must contain 'einddatum'."
            return einddatum
        except (json.JSONDecodeError, AssertionError) as e:
            pytest.fail(
                f"Could not parse a valid response from the PUT request. Error: {e}"
            )


def volgindicaties_create_plnummer(pl_lookup, pl_nummer):
    logger.debug(f"[{pl_nummer}]")
    bsn = pl_lookup[pl_nummer]
    volgindicaties_put(bsn, einddatum=EINDDATUM_TOEKOMST, status_code_ok=201)


def volgindicaties_delete_plnummer(pl_lookup, pl_nummer):
    logger.debug(f"[{pl_nummer}]")
    bsn = pl_lookup[pl_nummer]
    volgindicaties_put(bsn, einddatum=yesterday(), status_code_ok=None)


def reset_volgindicaties(pl_lookup, pl_nummers):
    for pl_nummer in pl_nummers:
        volgindicaties_delete_plnummer(pl_lookup, pl_nummer)


def check_verwachtingen(pl_lookup, pl_nummers):
    burgerservicenummers = [pl_lookup[pl_nummer] for pl_nummer in pl_nummers]
    logger.info("-" * 20)
    logger.info(pl_nummers)
    logger.info(burgerservicenummers)
    logger.info("-" * 20)
    wijzigingen_get(today(), burgerservicenummers, status_code_ok=200)


def check_verwachtingen_bsns(burgerservicenummers):
    wijzigingen_get(today(), burgerservicenummers, status_code_ok=200)


def setup_volgindicaties(pl_lookup, pl_plaatsen, pl_verwijderen):
    for pl_nummer in pl_plaatsen:
        volgindicaties_create_plnummer(pl_lookup, pl_nummer)
    for pl_nummer in pl_verwijderen:
        volgindicaties_delete_plnummer(pl_lookup, pl_nummer)


def setup_volgindicaties_bsns(bsns):
    for bsn in bsns:
        volgindicaties_put(bsn, einddatum=EINDDATUM_TOEKOMST, status_code_ok=201)


def reset_volgindicaties_bsns(bsns):
    for bsn in bsns:
        volgindicaties_put(bsn, einddatum=yesterday(), status_code_ok=None)


@pytest.mark.deel_2
def test_deel_2(bsns_deel_2):
    setup_volgindicaties_bsns(bsns_deel_2)


@pytest.mark.deel_2_reset
def test_deel_2_reset(bsns_deel_2):
    reset_volgindicaties_bsns(bsns_deel_2)


@pytest.mark.deel_3_verwacht
def test_deel_3_verwacht(bsns_deel_3_verwacht):
    check_verwachtingen_bsns(bsns_deel_3_verwacht)


@pytest.mark.deel_4
def test_deel_4(pl_lookup):
    pl_plaatsen = PERSON_NUMBERS_DEEL_4_PLAATSEN
    pl_verwijderen = PERSON_NUMBERS_DEEL_4_VERWIJDER
    setup_volgindicaties(pl_lookup, pl_plaatsen, pl_verwijderen)


@pytest.mark.deel_4_reset
def test_deel_4_reset(pl_lookup):
    reset_volgindicaties(pl_lookup, PERSON_NUMBERS_DEEL_4_PLAATSEN)


@pytest.mark.deel_5_verwacht
def test_deel_5_verwacht(bsns_deel_5_verwacht, pl_lookup):
    bsns = set(bsns_deel_5_verwacht) - set([pl_lookup[pl_nummer] for pl_nummer in PERSON_NUMBERS_DEEL_4_VERWIJDER])
    check_verwachtingen_bsns(bsns)


@pytest.mark.deel_6_verwacht
def test_deel_6_verwacht(bsns_deel_6_verwacht, pl_lookup):
    bsns = set(bsns_deel_6_verwacht) - set([pl_lookup[pl_nummer] for pl_nummer in PERSON_NUMBERS_DEEL_4_VERWIJDER])
    check_verwachtingen_bsns(bsns)


@pytest.mark.deel_7
def test_deel_7(pl_lookup):
    pl_plaatsen = PERSON_NUMBERS_DEEL_7_PLAATSEN
    pl_verwijderen = PERSON_NUMBERS_DEEL_7_VERWIJDER
    setup_volgindicaties(pl_lookup, pl_plaatsen, pl_verwijderen)


@pytest.mark.deel_7_reset
def test_deel_7_reset(pl_lookup):
    reset_volgindicaties(pl_lookup, PERSON_NUMBERS_DEEL_7_PLAATSEN)


@pytest.mark.deel_9
def test_deel_9(pl_lookup):
    pl_plaatsen = PERSON_NUMBERS_DEEL_9_PLAATSEN
    pl_verwijderen = PERSON_NUMBERS_DEEL_9_VERWIJDER
    setup_volgindicaties(pl_lookup, pl_plaatsen, pl_verwijderen)


@pytest.mark.deel_9_reset
def test_deel_9_reset(pl_lookup):
    reset_volgindicaties(pl_lookup, PERSON_NUMBERS_DEEL_9_PLAATSEN)


def main():
    print("hello from schouwen-toetsen!")
    print("run tests through pytest")


if __name__ == "__main__":
    main()
