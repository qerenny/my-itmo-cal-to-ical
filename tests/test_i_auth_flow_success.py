from __future__ import annotations

import pytest
from aioresponses import aioresponses
from aiohttp import ClientSession

import auth
from conftest import register_auth_flow


@pytest.mark.asyncio
async def test_get_access_token_success_flow():
    with aioresponses() as mocked:
        register_auth_flow(mocked, access_token="TOKEN123")
        async with ClientSession() as session:
            token = await auth.get_access_token(session, "user", "pass")
        total_calls = sum(len(calls) for calls in mocked.requests.values())

    assert token == "TOKEN123"
    assert total_calls == 3  # auth, form POST (302), token
