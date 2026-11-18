from django.conf import settings

from django.db import models

 

 

class QuizAttempt(models.Model):

    TEST_TYPES = [

        ("pretest", "Pretest"),

        ("posttest", "Post Test"),

    ]

 

    user = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

    )

    experiment = models.CharField(max_length=100)

    test_type = models.CharField(max_length=20, choices=TEST_TYPES)

    difficulty = models.CharField(max_length=20)

    score = models.PositiveIntegerField()

    total = models.PositiveIntegerField()

    answers = models.JSONField(default=dict)

    submitted_at = models.DateTimeField(auto_now_add=True)

 

    def __str__(self):

        name = self.user.username if self.user else "Anonymous"

        return f"{name} - {self.experiment} - {self.score}/{self.total}"

 

 

class CodeSubmission(models.Model):

    user = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

    )

    experiment = models.CharField(max_length=100)

    student_name = models.CharField(max_length=100, blank=True)

    code = models.TextField()

    submitted_at = models.DateTimeField(auto_now_add=True)

 

    def __str__(self):

        return f"{self.experiment} - {self.student_name or 'Anonymous'}"

 

 

class Feedback(models.Model):

    user = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

    )

    name = models.CharField(max_length=100, blank=True)

    rating = models.PositiveSmallIntegerField(

        choices=[(i, str(i)) for i in range(1, 6)]

    )

    comments = models.TextField()

    suggestions = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

 

    def __str__(self):

        return f"{self.name or 'Anonymous'} - {self.rating}/5"