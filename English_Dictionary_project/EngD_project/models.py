from django.contrib.auth.models import User
from django.db import models

class WordSearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # This is crucial
    word = models.CharField(max_length=100)
    meaning = models.TextField()
    synonyms = models.JSONField(blank=True, null=True)
    antonyms = models.JSONField(blank=True, null=True)
    pronunciation = models.CharField(max_length=100, blank=True, null=True)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.word} by {self.user.username}"
