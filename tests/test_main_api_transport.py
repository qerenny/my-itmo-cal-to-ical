import asyncio
from datetime import date
from unittest import TestCase
from unittest.mock import patch
import main_api   


class MainApiTransportTests(TestCase):
    def test__get_calendar_data_sends_bearer_and_params(self):
        # Arrange
        captured = {}

        class _RespOk:
            def raise_for_status(self): pass
            async def json(self): return {"ok": True}

        class _Sess:
            async def get(self, url, *, params=None, headers=None):
                captured["url"] = url
                captured["params"] = params
                captured["headers"] = headers
                return _RespOk()

        class _Pivot(date):
            @classmethod
            def today(cls): return cls(2023, 9, 1)

        with patch.object(main_api, "date", _Pivot):
            # Act
            result = asyncio.run(main_api._get_calendar_data(_Sess(), "TOKEN123", "/x"))

        # Assert
        self.assertEqual(result, {"ok": True})
        self.assertTrue(captured["url"].endswith("/x"))
        self.assertEqual(
            captured["params"],
            {"date_start": "2023-08-01", "date_end": "2024-07-31"},
        )
        self.assertEqual(captured["headers"]["Authorization"], "Bearer TOKEN123")
