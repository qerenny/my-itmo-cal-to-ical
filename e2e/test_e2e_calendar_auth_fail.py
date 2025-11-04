import json
import re

from aioresponses import aioresponses
from playwright.sync_api import sync_playwright

AUTH_URL = "https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/auth"
FORM_URL = "https://id.itmo.ru/auth/realms/itmo/login-actions/authenticate?session=ok"


EXPECTED_FORM_BODY = {"loginAction": FORM_URL}


def test_calendar_auth_form_failure(app_server, base_url, calendar_path):
    with aioresponses() as mocked:
        mocked.get(re.compile(rf"{AUTH_URL}.*"), body=json.dumps(EXPECTED_FORM_BODY))
        mocked.post(FORM_URL, status=200, body="fail")

        with sync_playwright() as p:
            request_context = p.request.new_context(base_url=base_url)
            try:
                response = request_context.get(calendar_path)
                status = response.status
                body = response.text()
            finally:
                request_context.dispose()

    assert 500 <= status < 600
    assert "Wrong Keycloak form response" in body