from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Room, Game

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'games_played', 'wins', 'losses', 'draws']

class RoomSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    players = UserSerializer(many=True, read_only=True)
    player_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Room
        fields = ['id', 'name', 'code', 'creator', 'players', 'player_count', 'status', 'created_at']
        read_only_fields = ['code', 'created_at']

class GameSerializer(serializers.ModelSerializer):
    player_x = UserSerializer(read_only=True)
    player_o = UserSerializer(read_only=True)
    winner = UserSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    
    class Meta:
        model = Game
        fields = ['id', 'room', 'player_x', 'player_o', 'current_turn', 'board', 'status', 'winner', 'created_at', 'finished_at']
        read_only_fields = ['created_at', 'finished_at']

class MakeMoveSerializer(serializers.Serializer):
    row = serializers.IntegerField(min_value=0, max_value=2)
    col = serializers.IntegerField(min_value=0, max_value=2)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user