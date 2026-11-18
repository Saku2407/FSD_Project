from django.db import models


class StudentRecord(models.Model):
    """A sample ORM record created when a student runs the experiment."""
    session_key = models.CharField(max_length=40, db_index=True)
    name = models.CharField(max_length=60)
    course = models.CharField(max_length=60)
    marks = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=4)
    skills = models.CharField(max_length=160)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.course}'


class LabFeedback(models.Model):
    KIND_CHOICES = [('rating', 'Rating'), ('bug', 'Bug report'), ('suggestion', 'Suggestion')]
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_kind_display()} ({self.created_at:%Y-%m-%d})'
