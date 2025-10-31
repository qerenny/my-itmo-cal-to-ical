from __future__ import annotations

import re

import pytest
from aioresponses import aioresponses
from aiohttp import ClientSession

import auth


@pytest.mark.asyncio
async def test_get_access_token_form_error():
    with aioresponses() as mocked:
        auth_url_pattern = re.compile(
            r"https://id\.itmo\.ru/auth/realms/itmo/protocol/openid-connect/auth.*"
        )
        bad_login_action = (
            "https://id.itmo.ru/auth/realms/itmo/login-actions/authenticate?session=bad"
        )
        mocked.get(auth_url_pattern, status=200, body=f'{{"loginAction":"{bad_login_action}"}}')

        mocked.post(bad_login_action, status=200, body="fail")

        async with ClientSession() as session:
            with pytest.raises(ValueError) as ei:
                await auth.get_access_token(session, "user", "bad")

    assert "Wrong Keycloak form response" in str(ei.value)
