from django.contrib import admin

from .models import CodeSubmission, Feedback, QuizAttempt

 

 

@admin.register(QuizAttempt)

class QuizAttemptAdmin(admin.ModelAdmin):

    list_display = (

        "user", "experiment", "test_type", "difficulty",

        "score", "total", "submitted_at"

    )

    list_filter = ("test_type", "difficulty", "experiment")

    search_fields = ("experiment", "user__username")

 

 

@admin.register(CodeSubmission)

class CodeSubmissionAdmin(admin.ModelAdmin):

    list_display = ("user", "experiment", "student_name", "submitted_at")

    search_fields = ("experiment", "student_name", "user__username")

 

 

@admin.register(Feedback)

class FeedbackAdmin(admin.ModelAdmin):

    list_display = ("user", "name", "rating", "submitted_at")

    list_filter = ("rating",)

    search_fields = ("name", "comments", "suggestions")