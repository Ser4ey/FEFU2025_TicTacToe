from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
import random

from .models import UserProfile, Room, Game
from .serializers import (
    UserSerializer, UserProfileSerializer, RoomSerializer, 
    GameSerializer, MakeMoveSerializer, RegisterSerializer
)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logout successful'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response(UserSerializer(request.user).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return Response(UserProfileSerializer(profile).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_list(request):
    rooms = Room.objects.filter(status__in=[Room.WAITING, Room.PLAYING]).order_by('-created_at')
    return Response(RoomSerializer(rooms, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_room(request):
    name = request.data.get('name', f"{request.user.username}'s room")
    room = Room.objects.create(name=name, creator=request.user)
    room.players.add(request.user)
    return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if room.status != Room.WAITING:
        return Response({'error': 'Room is not available'}, status=status.HTTP_400_BAD_REQUEST)
    
    if room.player_count >= 2:
        return Response({'error': 'Room is full'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.user in room.players.all():
        return Response({'error': 'Already in room'}, status=status.HTTP_400_BAD_REQUEST)
    
    room.players.add(request.user)
    
    # Start game if room is full
    if room.player_count == 2:
        room.status = Room.PLAYING
        room.save()
        
        # Create game
        players = list(room.players.all())
        random.shuffle(players)  # Randomly assign X and O
        
        Game.objects.create(
            room=room,
            player_x=players[0],
            player_o=players[1]
        )
    
    return Response(RoomSerializer(room).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_game(request):
    from django.db.models import Count
    
    # Find a waiting room with 1 player
    available_room = Room.objects.annotate(
        player_count_annotated=Count('players')
    ).filter(
        status=Room.WAITING,
        player_count_annotated=1
    ).exclude(players=request.user).first()
    
    if available_room:
        # Join existing room
        available_room.players.add(request.user)
        available_room.status = Room.PLAYING
        available_room.save()
        
        # Create game
        players = list(available_room.players.all())
        random.shuffle(players)
        
        Game.objects.create(
            room=available_room,
            player_x=players[0],
            player_o=players[1]
        )
        
        return Response({
            'room': RoomSerializer(available_room).data,
            'action': 'joined'
        })
    else:
        # Create new room
        room = Room.objects.create(
            name=f"{request.user.username}'s quick game",
            creator=request.user
        )
        room.players.add(request.user)
        
        return Response({
            'room': RoomSerializer(room).data,
            'action': 'created'
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.user not in room.players.all():
        return Response({'error': 'Not a player in this room'}, status=status.HTTP_403_FORBIDDEN)
    
    data = RoomSerializer(room).data
    
    # Add game data if exists
    try:
        game = room.game
        data['game'] = GameSerializer(game).data
    except Game.DoesNotExist:
        data['game'] = None
    
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_move(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.user not in room.players.all():
        return Response({'error': 'Not a player in this room'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        game = room.game
    except Game.DoesNotExist:
        return Response({'error': 'No active game'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = MakeMoveSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    row = serializer.validated_data['row']
    col = serializer.validated_data['col']
    
    success, message = game.make_move(row, col, request.user)
    
    if not success:
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update statistics if game finished
    if game.status != Game.ONGOING:
        game.finished_at = timezone.now()
        game.save()
        
        room.status = Room.FINISHED
        room.save()
        
        # Update player statistics
        for player in [game.player_x, game.player_o]:
            profile, created = UserProfile.objects.get_or_create(user=player)
            profile.games_played += 1
            
            if game.status == Game.DRAW:
                profile.draws += 1
            elif game.winner == player:
                profile.wins += 1
            else:
                profile.losses += 1
            
            profile.save()
    
    return Response({
        'message': message,
        'game': GameSerializer(game).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.user not in room.players.all():
        return Response({'error': 'Not in this room'}, status=status.HTTP_400_BAD_REQUEST)
    
    room.players.remove(request.user)
    
    # Delete room if empty
    if room.player_count == 0:
        room.delete()
        return Response({'message': 'Left room and room deleted'})
    
    # If game was in progress, end it
    if room.status == Room.PLAYING:
        try:
            game = room.game
            if game.status == Game.ONGOING:
                # Other player wins by forfeit
                other_player = room.players.first()
                game.winner = other_player
                game.status = Game.X_WINS if other_player == game.player_x else Game.O_WINS
                game.finished_at = timezone.now()
                game.save()
                
                # Update statistics
                winner_profile, _ = UserProfile.objects.get_or_create(user=other_player)
                loser_profile, _ = UserProfile.objects.get_or_create(user=request.user)
                
                winner_profile.games_played += 1
                winner_profile.wins += 1
                winner_profile.save()
                
                loser_profile.games_played += 1
                loser_profile.losses += 1
                loser_profile.save()
        except Game.DoesNotExist:
            pass
        
        room.status = Room.FINISHED
        room.save()
    
    return Response({'message': 'Left room'})