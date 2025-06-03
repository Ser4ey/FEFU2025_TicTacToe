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
#регистрация пользователя
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': 'Пользователь успешно создан'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    #логин, получаем из запроса данные и проверяем
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return Response({
            'message': 'Успешный вход',
            'user': UserSerializer(user).data
        })
    return Response({'error': 'Неверные данные'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    #разлогиниваем юзера
    logout(request)
    return Response({'message': 'Успешный выход'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response(UserSerializer(request.user).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    #получаем статистику
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return Response(UserProfileSerializer(profile).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_list(request):
    #получаем список комнат
    rooms = Room.objects.filter(status__in=[Room.WAITING, Room.PLAYING]).order_by('-created_at')
    return Response(RoomSerializer(rooms, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_room(request):
    #создаем новую комнату, имя по дефолту с ником пользователя
    name = request.data.get('name', f"Комната {request.user.username}")
    room = Room.objects.create(name=name, creator=request.user)
    room.players.add(request.user)
    return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_room(request, room_id):
    #подключаемся к комнате, если есть место и статус позволяет
    room = get_object_or_404(Room, id=room_id)
    
    if room.status != Room.WAITING:
        return Response({'error': 'Комната недоступна'}, status=status.HTTP_400_BAD_REQUEST)
    
    if room.player_count >= 2:
        return Response({'error': 'Комната заполнена'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.user in room.players.all():
        return Response({'error': 'Уже в комнате'}, status=status.HTTP_400_BAD_REQUEST)
    
    room.players.add(request.user)
    
    #если комната заполнилась начинаем игру
    if room.player_count == 2:
        room.status = Room.PLAYING
        room.save()

        Game.objects.filter(room=room).delete()

        #создание новой игры
        players = list(room.players.all())
        random.shuffle(players)

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
    
    #ищем свободную комнату с одним игроком
    available_room = Room.objects.annotate(
        player_count_annotated=Count('players')
    ).filter(
        status=Room.WAITING,
        player_count_annotated=1
    ).exclude(players=request.user).first()
    
    if available_room:
        #заходим в существующую комнату
        available_room.players.add(request.user)
        available_room.status = Room.PLAYING
        available_room.save()
        
        #создание игры
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
        #если нет подходящих комнат создаем новую
        room = Room.objects.create(
            name=f"Быстрая игра {request.user.username}",
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
    #возвращаем инфу о комнате (и игре если уже началась)
    room = get_object_or_404(Room, id=room_id)
    
    if request.user not in room.players.all():
        return Response({'error': 'Не является игроком в комнате'}, status=status.HTTP_403_FORBIDDEN)
    
    data = RoomSerializer(room).data
    
    #добавляем данные игры если она уже есть
    try:
        game = room.game
        data['game'] = GameSerializer(game).data
    except Game.DoesNotExist:
        data['game'] = None
    
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_move(request, room_id):
    #ход игрока в активной игре
    room = get_object_or_404(Room, id=room_id)
    
    if request.user not in room.players.all():
        return Response({'error': 'Не является игроком в комнате'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        game = room.game
    except Game.DoesNotExist:
        return Response({'error': 'Нет активной игры'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = MakeMoveSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    row = serializer.validated_data['row']
    col = serializer.validated_data['col']
    
    success, message = game.make_move(row, col, request.user)
    
    if not success:
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    #когда игра закончилась, обновляем статистику и статус игры
    if game.status != Game.ONGOING:
        game.finished_at = timezone.now()
        game.save()
        
        room.status = Room.FINISHED
        room.save()
        
        #статистика
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
        return Response({'error': 'Не является игроком в комнате'}, status=status.HTTP_400_BAD_REQUEST)

    #найдем связанную игру если она есть
    game = None
    try:
        game = room.game
    except Game.DoesNotExist:
        pass

    #если игра существует и была в процессе  начисляем победу/поражение и обновляем статистику
    if game and game.status == Game.ONGOING:
         other_player = room.players.exclude(id=request.user.id).first()
         if other_player:
            game.winner = other_player
            game.status = Game.X_WINS if other_player == game.player_x else Game.O_WINS
            game.finished_at = timezone.now()
            game.save()

            #обновляем статистику
            winner_profile, _ = UserProfile.objects.get_or_create(user=other_player)
            loser_profile, _ = UserProfile.objects.get_or_create(user=request.user)

            winner_profile.games_played += 1
            winner_profile.wins += 1
            winner_profile.save()

            loser_profile.games_played += 1
            loser_profile.losses += 1
            loser_profile.save()

    #удаляем объект игры, если он был найден
    if game:
        game.delete()

    room.players.remove(request.user) #удаляем игрока из комнаты ПОСЛЕ обработки статистики и игры

    #если комната пустая - удаляем её
    if room.player_count == 0:
        room.delete()
        return Response({'message': 'Вышел из комнаты, комната удалена'})

    # Если остался один игрок, переводим комнату в статус ожидания, чтобы другие могли зайти и поиграть
    if room.player_count == 1:
        room.status = Room.WAITING
        room.save()

    return Response({'message': 'Вышел из комнаты'})
