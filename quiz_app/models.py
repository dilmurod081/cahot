# quiz_app/models.py

import random
import string
from django.db import models

def generate_game_code():
    """Generates a unique 6-character code for a game."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Question(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.text[:30]}... -> {self.text}"

class Game(models.Model):
    STATUS_CHOICES = [
        ('joining', 'Joining'),
        ('in-progress', 'In Progress'),
        ('finished', 'Finished'),
    ]
    code = models.CharField(max_length=6, default=generate_game_code, unique=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='joining')
    current_question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, blank=True)
    question_start_time = models.DateTimeField(null=True, blank=True)
    host_session_key = models.CharField(max_length=40)

    def __str__(self):
        return f"Game {self.code} ({self.get_status_display()})"

class Player(models.Model):
    game = models.ForeignKey(Game, related_name='players', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    session_key = models.CharField(max_length=40, unique=True)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.name} in Game {self.game.code}"

class Answer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'question')