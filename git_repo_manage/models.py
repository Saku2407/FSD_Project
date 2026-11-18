from django.db import models


class LabFeedback(models.Model):
    KIND_CHOICES = [('rating', 'Rating'), ('bug', 'Bug report'), ('suggestion', 'Suggestion')]
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_kind_display()} ({self.created_at:%Y-%m-%d})'
