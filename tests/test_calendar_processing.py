from unittest import TestCase
from ics import Event   
from calendar_processing import build_calendar, calendar_to_ics_text   


class CalendarProcessingTests(TestCase):
    def test_build_calendar_adds_events_and_creator(self):
        # Arrange
        event = Event(name="Test", begin="2023-09-01 10:00:00", end="2023-09-01 12:00:00")
        event2 = Event(name="Test", begin="2023-09-01 10:00:00", end="2023-09-01 12:00:00")

        # Act
        calendar = build_calendar([event])

        # Assert
        self.assertEqual(calendar.creator, "my-itmo-ru-to-ical")
        self.assertEqual(len(calendar.events), 1)
        self.assertIn(event, calendar.events)
        self.assertNotIn(event2, calendar.events)

    def test_calendar_to_ics_text_contains_event_blocks(self):
        # Arrange
        event = Event(name="Test", begin="2023-09-01 10:00:00", end="2023-09-01 12:00:00")
        calendar = build_calendar([event])

        # Act
        ics_text = calendar_to_ics_text(calendar)

        # Assert
        self.assertIn("BEGIN:VCALENDAR", ics_text)
        self.assertIn("BEGIN:VEVENT", ics_text)
        self.assertIn("END:VEVENT", ics_text)
