from __future__ import annotations

import re

from aioresponses import aioresponses
from ics import Calendar

from conftest import register_auth_flow


def test_calendar_endpoint_returns_ics(configured_app):
    lessons_payload = {
        "data": [
            {
                "date": "2023-09-02",
                "lessons": [
                    {
                        "time_start": "12:00", 
                        "time_end": "10:00",
                        "subject": "Математика",
                        "type": "Лекции",
                        "room": "Ауд. 101",
                        "building": "Главный корпус",
                        "group": "3100",
                        "teacher_name": "Иван Иванов",
                        "zoom_url": "https://zoom.example/meeting",
                        "zoom_password": "zpass",
                        "zoom_info": "",
                        "note": "принести тетрадь",
                    }
                ],
            }
        ]
    }

    with aioresponses() as mocked:
        register_auth_flow(mocked, access_token="ACCESS_TOKEN")
        mocked.get(
            re.compile(r"https://my\.itmo\.ru/api/schedule/schedule/personal.*"),
            status=200,
            payload=lessons_payload,
        )

        with configured_app.app.test_client() as client:
            resp = client.get(configured_app._calendar_route)

    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("text/calendar")

    calendar_text = resp.get_data(as_text=True)
    assert "BEGIN:VCALENDAR" in calendar_text
    assert calendar_text.count("BEGIN:VEVENT") >= 1

    cal = Calendar(calendar_text)
    events = list(cal.events)
    assert len(events) == 1
    [event] = events

    assert event.name == "[Лек] Математика"
    assert event.location == "Zoom / Ауд. 101, Главный корпус"
    assert "Группа: 3100" in event.description
    assert event.begin <= event.end
