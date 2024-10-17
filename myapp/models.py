from django.db import models
from django.db.models import Count, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce


class Event(models.Model):
    """
    An event has at least 1 session.
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Session(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PromoterQuerySet(models.QuerySet):
    def with_nb_events(self):
        """
        Return the number of distinct events this promoter was
        assigned to, either through sessions or through events
        directly.
        """
        return self.annotate(
            nb_events=Coalesce(
                Subquery(
                    Session.objects.filter(
                        Q(
                            pk__in=Promoter.sessions.through.objects.filter(
                                promoter_id=OuterRef(OuterRef("pk"))
                            ).values_list("session_id")
                        )
                        | Q(
                            event_id__in=Promoter.events.through.objects.filter(
                                promoter_id=OuterRef(OuterRef("pk"))
                            ).values_list("event_id")
                        )
                    )
                    .order_by()
                    # This gets rid of the `GROUP BY id` that Django generates
                    # (we need the count over the whole set, not per row)
                    .values_list(Value(None))
                    # We can’t use aggregate in subqueries so we annotate and
                    # limit to 1 result
                    .annotate(nb=Count("event_id", distinct=True))
                    .values_list("nb")[:1]
                ),
                Value(0),
            )
        )


class Promoter(models.Model):
    email = models.EmailField()
    sessions = models.ManyToManyField(Session)
    events = models.ManyToManyField(Event)

    objects = PromoterQuerySet.as_manager()

    def __str__(self):
        return self.email
