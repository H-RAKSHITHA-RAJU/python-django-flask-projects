from django.contrib import admin
from .models import WordSearchHistory

@admin.register(WordSearchHistory)
class WordSearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('word', 'user', 'searched_at')
    search_fields = ('word', 'user__username')
    list_filter = ('searched_at',)
    ordering = ('-searched_at',)
