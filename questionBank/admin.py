# questionBank/admin.py

from django.contrib import admin
from .models import Subject, Question, Option, UserResponse, Result

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'text', 'correct_option')
    search_fields = ('text',)
    list_filter = ('subject',)
    raw_id_fields = ('correct_option',)

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text')
    search_fields = ('text',)
    list_filter = ('question',)

@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'selected_option', 'timestamp')
    search_fields = ('user__username', 'question__text', 'selected_option__text')
    list_filter = ('timestamp',)

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'score', 'speed', 'timestamp')
    search_fields = ('user__username', 'subject__name')
    list_filter = ('timestamp',)

