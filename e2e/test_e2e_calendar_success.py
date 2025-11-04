import json
import re

from aioresponses import aioresponses
from ics import Calendar
from playwright.sync_api import sync_playwright

AUTH_URL = "https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/auth"
FORM_URL = "https://id.itmo.ru/auth/realms/itmo/login-actions/authenticate?session=ok"
TOKEN_URL = "https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/token"
SCHEDULE_URL = "https://my.itmo.ru/api/schedule/schedule/personal"


LESSON_PAYLOAD = {
    "data": [
        {
            "date": "2023-09-01",
            "lessons": [
                {
                    "subject": "Математика",
                    "type": "Лекции",
                    "time_start": "12:00",
                    "time_end": "10:00",
                    "zoom_url": "https://zoom.example.com/lesson",
                    "room": "101",
                    "building": "Главный корпус",
                    "group": "M3230",
                    "teacher_name": "Иванов И.И.",
                }
            ],
        }
    ]
}


EXPECTED_FORM_BODY = {"loginAction": FORM_URL}


def test_calendar_happy_path(app_server, base_url, calendar_path):
    with aioresponses() as mocked:
        mocked.get(re.compile(rf"{AUTH_URL}.*"), body=json.dumps(EXPECTED_FORM_BODY))
        mocked.post(FORM_URL, status=302, headers={"Location": "https://my.itmo.ru/login/callback?code=AUTH_CODE"})
        mocked.post(TOKEN_URL, payload={"access_token": "TOKEN123"})
        mocked.get(re.compile(rf"{SCHEDULE_URL}.*"), payload=LESSON_PAYLOAD)

        with sync_playwright() as p:
            request_context = p.request.new_context(base_url=base_url)
            try:
                response = request_context.get(calendar_path)
                status = response.status
                headers = response.headers
                body = response.text()
            finally:
                request_context.dispose()

    assert status == 200
    content_type = headers.get("content-type", "")
    content_type = response.headers.get("content-type", "")
    assert content_type.startswith("text/calendar")

    assert "BEGIN:VCALENDAR" in body
    assert body.count("BEGIN:VEVENT") >= 1
    assert "[Лек]" in body
    assert "URL:" in body
    assert "LOCATION:" in body

    calendar = Calendar(body)
    assert calendar.events
    for event in calendar.events:
        assert event.begin <= event.end