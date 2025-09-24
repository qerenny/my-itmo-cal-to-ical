from datetime import datetime
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch
import lessons_to_events
from lessons_to_events import (   
    _raw_lesson_to_description,
    _raw_lesson_to_location,
    _raw_lesson_to_uuid,
    raw_lesson_to_event,
)


class LessonTransformationTests(TestCase):
    def test_raw_lesson_to_location_prefers_zoom_with_room(self):
        # Arrange
        raw_lesson = {
            "room": "4201",
            "building": "Кронверкский пр., 49",
            "zoom_url": "https://zoom.itmo.example",
        }

        # Act
        location = _raw_lesson_to_location(raw_lesson)

        # Assert
        self.assertEqual(location, "Zoom / 4201, Кронверкский пр., 49")

    def test_raw_lesson_to_location_returns_none_when_empty(self):
        # Arrange
        raw_lesson: Dict[str, Any] = {}

        # Act
        location = _raw_lesson_to_location(raw_lesson)

        # Assert
        self.assertIsNone(location)

    def test_raw_lesson_to_description_formats_known_fields(self):
        # Arrange
        raw_lesson = {
            "group": "К3441",
            "teacher_name": "Иванов И.И.",
            "zoom_info": "12345",
            "note": "Придите пожалуйста",
        }

        class _FixedDatetime(datetime):
            @classmethod
            def utcnow(cls):
                return cls(2023, 1, 1, 10, 0, 0)

        with patch.object(lessons_to_events, "datetime", _FixedDatetime):
            # Act
            description = _raw_lesson_to_description(raw_lesson)

        # Assert
        expected_lines = [
            "Группа: К3441",
            "Преподаватель: Иванов И.И.",
            "Доп. информация для Zoom: 12345",
            "Примечание: Придите пожалуйста",
            "Обновлено: 2023-01-01 13:00 MSK",
        ]
        self.assertEqual(description.splitlines(), expected_lines)

    def test_raw_lesson_to_uuid_is_stable(self):
        # Arrange
        raw_lesson = {
            "date": "2023-09-01",
            "time_start": "08:20",
            "subject": "Тестирование программного обеспечения",
        }
        expected_uuid = "ac101128-d8f6-1ca1-dcd9-437dbf57cb9b"

        # Act
        result_uuid = _raw_lesson_to_uuid(raw_lesson)

        # Assert
        self.assertEqual(result_uuid, expected_uuid)

    def test_raw_lesson_to_event_swaps_inverted_times(self):
        # Arrange
        raw_lesson = {
            "date": "2023-09-01",
            "time_start": "12:00",
            "time_end": "10:00",
            "type": "Лекции",
            "subject": "Тестирование программного обеспечения",
            "group": "",
            "teacher_name": "",
            "teacher_fio": "",
            "zoom_url": "https://zoom.itmo.example",
            "zoom_password": "",
            "zoom_info": "",
            "note": "",
            "room": "",
            "building": "",
        }

        # Act
        event = raw_lesson_to_event(raw_lesson)

        # Assert
        self.assertLessEqual(event.begin.datetime, event.end.datetime)
        self.assertEqual(event.name, "[Лек] Тестирование программного обеспечения")
        self.assertEqual(event.url, "https://zoom.itmo.example")
