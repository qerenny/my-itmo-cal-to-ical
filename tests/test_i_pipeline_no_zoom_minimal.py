from __future__ import annotations

import calendar_processing
import lessons_to_events


def test_pipeline_without_zoom_fields():
    raw_lesson = {
        "date": "2024-09-10",
        "time_start": "12:00",
        "time_end": "13:30",
        "subject": "История",
        "type": "Практические занятия",
        "room": "",
        "building": "",
        "group": "3100",
        "teacher_name": "Анна Смирнова",
        "zoom_url": "",
        "zoom_password": "",
        "zoom_info": "",
        "note": "",
    }

    event = lessons_to_events.raw_lesson_to_event(raw_lesson)
    calendar = calendar_processing.build_calendar([event])
    ics_text = calendar_processing.calendar_to_ics_text(calendar)

    assert "URL:" not in ics_text
    assert "LOCATION" not in ics_text
    assert "[Прак] История" in ics_text
    assert "Обновлено:" in ics_text and "MSK" in ics_text
