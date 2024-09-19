from django.contrib import admin
from .models import Subject, Worksheet, Question, TestSession, UserResponse, Result

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Worksheet)
class WorksheetAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'name', 'file_path')
    search_fields = ('name', 'subject__name')
    list_filter = ('subject',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'worksheet', 'text', 'correct_option', 'order')
    list_display_links = ('id', 'text')
    search_fields = ('text', 'worksheet__name', 'worksheet__subject__name')
    list_filter = ('worksheet__subject', 'worksheet', 'correct_option')
    fieldsets = (
        (None, {
            'fields': ('worksheet', 'text', 'order', 'image')
        }),
        ('Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_option')
        }),
    )

@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'start_time', 'end_time', 'score', 'completed')
    search_fields = ('user__username',)
    list_filter = ('completed', 'subjects')

@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'selected_option', 'is_correct', 'timestamp')
    search_fields = ('user__username', 'question__text')
    list_filter = ('selected_option', 'question__worksheet__subject', 'question__worksheet')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'worksheet', 'score', 'speed', 'timestamp')
    search_fields = ('user__username', 'subject__name', 'worksheet__name')
    list_filter = ('subject', 'worksheet', 'timestamp')