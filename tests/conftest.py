from __future__ import annotations

import importlib
import json
import re
import sys
from typing import Iterator

import pytest

import auth


def _clear_async_ttl_cache(func):
    """Очистка кэша для декоратора AsyncTTL в auth.get_access_token."""
    closure = getattr(func, "__closure__", None)
    if not closure:
        return
    for cell in closure:
        obj = cell.cell_contents
        if hasattr(obj, "ttl"):
            obj.ttl.clear()
            break


@pytest.fixture(autouse=True)
def clear_access_token_cache():
    _clear_async_ttl_cache(auth.get_access_token)
    yield
    _clear_async_ttl_cache(auth.get_access_token)


@pytest.fixture
def configured_app(monkeypatch):
    # Готовим окружение до импорта app
    monkeypatch.setenv("ITMO_ICAL_ISU_USERNAME", "student")
    monkeypatch.setenv("ITMO_ICAL_ISU_PASSWORD", "password")
    monkeypatch.delenv("ITMO_ICAL_SENTRY_DSN", raising=False)

    # Переимпорт, чтобы конфиг подтянулся из env
    sys.modules.pop("app", None)
    app_module = importlib.import_module("app")
    return app_module


def register_auth_flow(mocked, access_token: str = "ACCESS_TOKEN"):
    """Полный успешный PKCE/Keycloak-поток для aioresponses."""
    auth_url_pattern = re.compile(
        r"https://id\.itmo\.ru/auth/realms/itmo/protocol/openid-connect/auth.*"
    )
    login_action_url = (
        "https://id.itmo.ru/auth/realms/itmo/login-actions/authenticate?session_code=session"
    )

    mocked.get(auth_url_pattern, status=200, body=json.dumps({"loginAction": login_action_url}))
    mocked.post(
        re.compile(r"https://id\.itmo\.ru/auth/realms/itmo/login-actions/authenticate.*"),
        status=302,
        headers={"Location": "https://my.itmo.ru/login/callback?code=AUTH_CODE"},
    )
    mocked.post(
        "https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/token",
        status=200,
        payload={"access_token": access_token},
    )


def find_calls(mocked, method: str, url_substring: str):
    """Надёжно достаёт список вызовов по методу и части URL из aioresponses."""
    for (m, url), calls in mocked.requests.items():
        if m == method and url_substring in str(url):
            return calls
    return []
