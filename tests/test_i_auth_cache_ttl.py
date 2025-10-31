from __future__ import annotations

import pytest
from aioresponses import aioresponses
from aiohttp import ClientSession

import auth
from conftest import register_auth_flow


@pytest.mark.asyncio
async def test_get_access_token_uses_cache():
    # Первый вызов — наполняем кэш
    with aioresponses() as mocked:
        register_auth_flow(mocked, access_token="CACHED")
        async with ClientSession() as session:
            first = await auth.get_access_token(session, "user", "pass")
    assert first == "CACHED"

    # Второй вызов — без сети
    class _FailingSession:
        async def get(self, *_, **__):  
            raise AssertionError("Should not perform GET when cached")
        async def post(self, *_, **__):  
            raise AssertionError("Should not perform POST when cached")

    second = await auth.get_access_token(_FailingSession(), "user", "pass")
    assert second == "CACHED"
