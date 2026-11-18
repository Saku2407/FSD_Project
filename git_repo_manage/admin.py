from django.contrib import admin
from .models import LabFeedback


@admin.register(LabFeedback)
class LabFeedbackAdmin(admin.ModelAdmin):
    list_display = ('kind', 'rating', 'created_at')
    list_filter = ('kind',)
