"""Script base de proves creuades per a la Sessio 7.

Cada grup l'ha d'adaptar i lliurar com a:
  sd2526_G1_G2.py
on:
  G1 = codi del grup que avalua
  G2 = codi del grup que s'avalua

Execucio local:
    pytest scripts/sd2526_test.py -v

Execucio recomanada:
    docker compose -f docker-compose.tests.yml up --abort-on-container-exit

Dependencia:
  pip install pytest requests
"""

import os
import time
from typing import Any

import pytest
import requests

BASE_URL = os.getenv("BASE_API_URL") or os.getenv("BASE_URL", "http://localhost:8000")

REGISTER_ENDPOINT = os.getenv("REGISTER_ENDPOINT", "/api/v1/users/")
LOGIN_ENDPOINT = os.getenv("LOGIN_ENDPOINT", "/api/v1/token/")
USERS_LIST_ENDPOINT = os.getenv("USERS_LIST_ENDPOINT", "/api/v1/users/")
USER_DETAIL_ENDPOINT_TEMPLATE = os.getenv("USER_DETAIL_ENDPOINT_TEMPLATE", "/api/v1/users/{user_id}/")
EVENTS_ENDPOINT = os.getenv("EVENTS_ENDPOINT", "/api/v1/events/")
EVENT_DETAIL_ENDPOINT_TEMPLATE = os.getenv("EVENT_DETAIL_ENDPOINT_TEMPLATE", "/api/v1/events/{event_id}/")
CHECKOUT_ENDPOINT = os.getenv("CHECKOUT_ENDPOINT", "/api/v1/checkout/")

ALLOW_NON_ADMIN_EVENT_CREATE = os.getenv("ALLOW_NON_ADMIN_EVENT_CREATE", "false").lower() == "true"

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

REQUEST_TIMEOUT = 15


def _url(path: str) -> str:
    return f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}"


def _token_from_login_response(data: dict[str, Any]) -> str | None:
    for key in ("access", "token", "access_token"):
        if key in data and data[key]:
            return data[key]
    return None


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _unique_user(prefix: str) -> dict[str, str]:
    suffix = str(int(time.time() * 1000))[-8:]
    username = f"{prefix}_{suffix}"
    return {
        "username": username,
        "password": "TestPass123!",
        "email": f"{username}@example.com",
    }


def _register_payload(user: dict[str, str]) -> dict[str, str]:
    # Adapteu els camps si la API del grup usa una estructura diferent.
    return {
        "username": user["username"],
        "password": user["password"],
        "email": user["email"],
    }


def _login_payload(user: dict[str, str]) -> dict[str, str]:
    # Adapteu els camps si la API demana "username", "email" o un altre identificador.
    return {
        "username": user["username"],
        "password": user["password"],
    }


def _event_payload() -> dict[str, Any]:
    # Plantilla orientativa. Ajusteu noms de camps segons el grup avaluat.
    return {
        "nom": "Concert prova SD2526",
        "descripcio": "Esdeveniment de prova creuada",
        "data": "2026-06-15T19:00:00Z",
        "aforament": 10,
        "preu": "25.00",
    }


def _checkout_ok_payload(event_id: int) -> dict[str, Any]:
    # Adapteu estructura i noms de camps segons l'API del grup avaluat.
    return {
        "entrades": [
            {"esdeveniment_id": event_id, "quantitat": 1},
        ]
    }


def _checkout_insufficient_payload(event_id: int) -> dict[str, Any]:
    return {
        "entrades": [
            {"esdeveniment_id": event_id, "quantitat": 9999},
        ]
    }


@pytest.fixture(scope="module")
def http() -> requests.Session:
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope="module")
def users() -> dict[str, dict[str, str]]:
    return {
        "normal_a": _unique_user("normal_a"),
        "normal_b": _unique_user("normal_b"),
    }


def _register_user(http: requests.Session, user: dict[str, str]) -> requests.Response:
    return http.post(
        _url(REGISTER_ENDPOINT),
        json=_register_payload(user),
        timeout=REQUEST_TIMEOUT,
    )


def _login_user(http: requests.Session, user: dict[str, str]) -> tuple[requests.Response, str | None]:
    response = http.post(
        _url(LOGIN_ENDPOINT),
        json=_login_payload(user),
        timeout=REQUEST_TIMEOUT,
    )
    token = None
    if response.headers.get("content-type", "").startswith("application/json"):
        token = _token_from_login_response(response.json())
    return response, token


@pytest.fixture(scope="module")
def registered_users(http: requests.Session, users: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    for user in users.values():
        response = _register_user(http, user)
        assert response.status_code in (200, 201), (
            f"Error en registre d'usuari {user['username']}: {response.status_code} {response.text}"
        )
    return users


@pytest.fixture(scope="module")
def normal_tokens(
    http: requests.Session,
    registered_users: dict[str, dict[str, str]],
) -> dict[str, str]:
    tokens: dict[str, str] = {}
    for key, user in registered_users.items():
        response, token = _login_user(http, user)
        assert response.status_code in (200, 201), (
            f"Error de login per {user['username']}: {response.status_code} {response.text}"
        )
        assert token, f"No s'ha rebut token al login de {user['username']}"
        tokens[key] = token
    return tokens


@pytest.fixture(scope="module")
def admin_token(http: requests.Session) -> str:
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        pytest.skip("No hi ha ADMIN_USERNAME/ADMIN_PASSWORD configurats per provar flux admin")

    response = http.post(
        _url(LOGIN_ENDPOINT),
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code in (200, 201), f"Login admin fallit: {response.status_code} {response.text}"

    token = _token_from_login_response(response.json())
    assert token, "No s'ha rebut token d'admin"
    return token


@pytest.fixture(scope="module")
def created_event_id(http: requests.Session, admin_token: str) -> int:
    response = http.post(
        _url(EVENTS_ENDPOINT),
        json=_event_payload(),
        headers=_auth_headers(admin_token),
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code in (200, 201), f"No s'ha pogut crear esdeveniment amb admin: {response.status_code} {response.text}"

    data = response.json()
    event_id = data.get("id")
    assert event_id is not None, "La resposta de creacio d'esdeveniment no inclou id"
    return int(event_id)


# T01

def test_t01_registre_usuari_correcte(http: requests.Session) -> None:
    user = _unique_user("t01")
    response = _register_user(http, user)
    assert response.status_code in (200, 201), response.text


# T02

def test_t02_login_correcte(http: requests.Session) -> None:
    user = _unique_user("t02")
    register_response = _register_user(http, user)
    assert register_response.status_code in (200, 201), register_response.text

    login_response, token = _login_user(http, user)
    assert login_response.status_code in (200, 201), login_response.text
    assert token, login_response.text


# T03

def test_t03_acces_endpoint_protegit_sense_token(http: requests.Session) -> None:
    response = http.get(_url(USERS_LIST_ENDPOINT), timeout=REQUEST_TIMEOUT)
    assert response.status_code in (401, 403), response.text


# T04

def test_t04_llista_usuaris_sense_autenticacio(http: requests.Session) -> None:
    response = http.get(_url(USERS_LIST_ENDPOINT), timeout=REQUEST_TIMEOUT)
    assert response.status_code in (401, 403), response.text


# T05

def test_t05_modificacio_usuari_sense_autenticacio(
    http: requests.Session,
    registered_users: dict[str, dict[str, str]],
) -> None:
    # Adapteu l'id d'usuari si la API no el retorna o no usa aquest endpoint.
    target_id = 1
    payload = {"email": registered_users["normal_a"]["email"].replace("@", "+edit@")}  # canvi simple

    response = http.patch(
        _url(USER_DETAIL_ENDPOINT_TEMPLATE.format(user_id=target_id)),
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code in (401, 403), response.text


# T06

def test_t06_modificar_altre_usuari_sense_permis(
    http: requests.Session,
    normal_tokens: dict[str, str],
) -> None:
    # Adapteu user_id objectiu segons la vostra API.
    target_id = 1
    payload = {"email": "hijack@example.com"}

    response = http.patch(
        _url(USER_DETAIL_ENDPOINT_TEMPLATE.format(user_id=target_id)),
        json=payload,
        headers=_auth_headers(normal_tokens["normal_a"]),
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code in (401, 403), response.text


# T07

def test_t07_modificar_propies_dades(
    http: requests.Session,
    normal_tokens: dict[str, str],
) -> None:
    # Si la vostra API no admet autoedició d'aquest camp, adapteu payload i endpoint.
    target_id = 1
    payload = {"email": "self_update@example.com"}

    response = http.patch(
        _url(USER_DETAIL_ENDPOINT_TEMPLATE.format(user_id=target_id)),
        json=payload,
        headers=_auth_headers(normal_tokens["normal_a"]),
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code in (200, 202, 204, 401, 403), response.text


# T08

def test_t08_modificar_capacitat_esdeveniment_usuari_normal(
    http: requests.Session,
    normal_tokens: dict[str, str],
    created_event_id: int,
) -> None:
    payload = {"aforament": 999}

    response = http.patch(
        _url(EVENT_DETAIL_ENDPOINT_TEMPLATE.format(event_id=created_event_id)),
        json=payload,
        headers=_auth_headers(normal_tokens["normal_a"]),
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code in (401, 403), response.text


# T09

def test_t09_alta_esdeveniment_usuari_no_privilegiat(
    http: requests.Session,
    normal_tokens: dict[str, str],
) -> None:
    response = http.post(
        _url(EVENTS_ENDPOINT),
        json=_event_payload(),
        headers=_auth_headers(normal_tokens["normal_a"]),
        timeout=REQUEST_TIMEOUT,
    )

    if ALLOW_NON_ADMIN_EVENT_CREATE:
        assert response.status_code in (200, 201), response.text
    else:
        assert response.status_code in (401, 403), response.text


# T10

def test_t10_alta_esdeveniment_usuari_privilegiat(
    http: requests.Session,
    admin_token: str,
) -> None:
    response = http.post(
        _url(EVENTS_ENDPOINT),
        json=_event_payload(),
        headers=_auth_headers(admin_token),
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code in (200, 201), response.text


# T11

def test_t11_compra_correcta_estoc_suficient(
    http: requests.Session,
    normal_tokens: dict[str, str],
    created_event_id: int,
) -> None:
    response = http.post(
        _url(CHECKOUT_ENDPOINT),
        json=_checkout_ok_payload(created_event_id),
        headers=_auth_headers(normal_tokens["normal_a"]),
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code in (200, 201), response.text


# T12

def test_t12_compra_fallida_estoc_insuficient(
    http: requests.Session,
    normal_tokens: dict[str, str],
    created_event_id: int,
) -> None:
    response = http.post(
        _url(CHECKOUT_ENDPOINT),
        json=_checkout_insufficient_payload(created_event_id),
        headers=_auth_headers(normal_tokens["normal_a"]),
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code in (400, 409, 422), response.text


# T13

def test_t13_compra_segon_usuari_sobre_esdeveniment(
    http: requests.Session,
    normal_tokens: dict[str, str],
    created_event_id: int,
) -> None:
    response = http.post(
        _url(CHECKOUT_ENDPOINT),
        json=_checkout_ok_payload(created_event_id),
        headers=_auth_headers(normal_tokens["normal_b"]),
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code in (200, 201), response.text
