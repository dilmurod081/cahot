# quiz_app/admin.py

from django.contrib import admin
from .models import Question, Choice, Game, Player

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1 # Start with one extra choice field

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('text',)

class PlayerInline(admin.TabularInline):
    model = Player
    readonly_fields = ('name', 'session_key', 'score')
    extra = 0

class GameAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]
    list_display = ('code', 'status', 'current_question', 'host_session_key')
    readonly_fields = ('code', 'host_session_key', 'question_start_time')

admin.site.register(Question, QuestionAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Player)