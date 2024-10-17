import logging

from django.test import TestCase

from .models import Event, Promoter, Session

logger = logging.getLogger(__name__)


class TestWithNbEvents(TestCase):
    def test_nb_events_is_correct(self):
        events = [
            Event.objects.create(name="event one"),
            Event.objects.create(name="event two"),
            Event.objects.create(name="event three"),
        ]

        sessions = [
            Session.objects.create(name="session one", event=events[0]),
            Session.objects.create(name="session two", event=events[0]),
            Session.objects.create(name="session three", event=events[1]),
        ]
        Session.objects.create(name="session four", event=events[2])

        promoter = Promoter.objects.create(email="foo@bar.com")
        promoter.sessions.set(sessions)
        promoter.events.set([events[1], events[2]])

        logger.warning(Promoter.objects.with_nb_events().query)

        self.assertEqual(Promoter.objects.with_nb_events().get().nb_events, 3)
