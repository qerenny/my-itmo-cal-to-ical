import asyncio
from datetime import date
from unittest import TestCase
from unittest.mock import AsyncMock, patch
import main_api   


class MainApiHelpersTests(TestCase):
    def test_get_date_range_params_before_august_first(self):
        # Arrange
        class _BeforePivot(date):
            @classmethod
            def today(cls):
                return cls(2023, 7, 1)

        with patch.object(main_api, "date", _BeforePivot):
            # Act
            params = main_api._get_date_range_params()

        # Assert
        self.assertEqual(
            params,
            {"date_start": "2022-08-01", "date_end": "2023-07-31"},
        )
        
    def test_get_date_range_params_on_august_first(self):
        # Arrange
        class _OnPivot(date):
            @classmethod
            def today(cls): return cls(2023, 8, 1)

        with patch.object(main_api, "date", _OnPivot):
            # Act
            params = main_api._get_date_range_params()

        # Assert
        self.assertEqual(
            params,
            {"date_start": "2023-08-01", "date_end": "2024-07-31"},
        )

    def test_get_date_range_params_after_august_first(self):
        # Arrange
        class _AfterPivot(date):
            @classmethod
            def today(cls):
                return cls(2023, 9, 1)

        with patch.object(main_api, "date", _AfterPivot):
            # Act
            params = main_api._get_date_range_params()

        # Assert
        self.assertEqual(
            params,
            {"date_start": "2023-08-01", "date_end": "2024-07-31"},
        )

    def test_get_raw_lessons_flattens_days(self):
        # Arrange
        response = {
            "data": [
                {
                    "date": "2023-09-01",
                    "lessons": [
                        {"subject": "Math", "time_start": "10:00", "time_end": "11:30"},
                        {"subject": "Physics", "time_start": "12:00", "time_end": "13:30"},
                    ],
                },
                {
                    "date": "2023-09-02",
                    "lessons": [
                        {"subject": "History", "time_start": "09:00", "time_end": "10:30"},
                    ],
                },
            ]
        }
        with patch.object(main_api, "_get_calendar_data", new_callable=AsyncMock) as get_calendar_mock:
            get_calendar_mock.return_value = response
            session = object()
            token = "token"

            # Act
            lessons_iterable = asyncio.run(main_api.get_raw_lessons(session, token))
            lessons = list(lessons_iterable)

        # Assert
        get_calendar_mock.assert_awaited_once_with(session, token, "/schedule/schedule/personal")
        self.assertEqual(len(lessons), 3)
        self.assertEqual(lessons[0]["date"], "2023-09-01")
        self.assertEqual(lessons[1]["subject"], "Physics")
        self.assertEqual(lessons[2]["date"], "2023-09-02")
