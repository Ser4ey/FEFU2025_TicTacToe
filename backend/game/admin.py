from django.contrib import admin
from .models import UserProfile, Room, Game

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'games_played', 'wins', 'losses', 'draws']
    list_filter = ['games_played', 'wins']
    search_fields = ['user__username']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'creator', 'player_count', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'code', 'creator__username']
    readonly_fields = ['code', 'created_at']

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['room', 'player_x', 'player_o', 'current_turn', 'status', 'winner', 'created_at']
    list_filter = ['status', 'current_turn', 'created_at']
    search_fields = ['room__name', 'player_x__username', 'player_o__username']
    readonly_fields = ['created_at', 'finished_at']