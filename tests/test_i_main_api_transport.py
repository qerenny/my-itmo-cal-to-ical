from __future__ import annotations

import re
from datetime import date

import pytest
from aioresponses import aioresponses
from aiohttp import ClientSession

import main_api
from conftest import find_calls


@pytest.mark.asyncio
async def test_get_raw_lessons_combines_days_and_sets_headers_params(monkeypatch):
    class _FixedDate(date):
        @classmethod
        def today(cls):
            return cls(2024, 3, 15)

    monkeypatch.setattr(main_api, "date", _FixedDate)

    payload = {
        "data": [
            {
                "date": "2024-09-02",
                "lessons": [
                    {"time_start": "10:00", "time_end": "11:30", "subject": "Алгебра", "type": "Лекции"},
                ],
            },
            {
                "date": "2024-09-03",
                "lessons": [
                    {"time_start": "08:00", "time_end": "09:30", "subject": "Физика", "type": "Лаб"},
                ],
            },
        ]
    }

    with aioresponses() as mocked:
        mocked.get(
            re.compile(r"https://my\.itmo\.ru/api/schedule/schedule/personal.*"),
            payload=payload,
            status=200,
        )
        async with ClientSession() as session:
            lessons_iter = await main_api.get_raw_lessons(session, "TOKEN")
            lessons = list(lessons_iter)

        calls = find_calls(mocked, "GET", "schedule/schedule/personal")
        assert calls, "Expected GET call to schedule endpoint"

    # Убедимся, что flatten сработал
    assert [l["subject"] for l in lessons] == ["Алгебра", "Физика"]

    # Проверяем параметры и заголовки на первом вызове
    called_params = calls[0].kwargs["params"]
    assert called_params == {"date_start": "2023-08-01", "date_end": "2024-07-31"}
    assert calls[0].kwargs["headers"]["Authorization"] == "Bearer TOKEN"
