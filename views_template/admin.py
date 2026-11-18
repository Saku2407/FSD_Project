from django.contrib import admin
from .models import StudentRecord, LabFeedback

@admin.register(StudentRecord)
class StudentRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'marks', 'status', 'created_at')
    list_filter = ('status', 'course')

@admin.register(LabFeedback)
class LabFeedbackAdmin(admin.ModelAdmin):
    list_display = ('kind', 'rating', 'created_at')
    list_filter = ('kind',)
