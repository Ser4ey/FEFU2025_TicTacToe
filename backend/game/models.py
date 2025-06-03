from django.db import models
from django.contrib.auth.models import User
import random
import string

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    games_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - W:{self.wins} L:{self.losses} D:{self.draws}"

class Room(models.Model):
    WAITING = 'waiting'
    PLAYING = 'playing'
    FINISHED = 'finished'
    
    STATUS_CHOICES = [
        (WAITING, 'Waiting'),
        (PLAYING, 'Playing'),
        (FINISHED, 'Finished'),
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    players = models.ManyToManyField(User, related_name='joined_rooms', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=WAITING)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Room {self.name} ({self.code})"
    
    @property
    def player_count(self):
        return self.players.count()

class Game(models.Model):
    X = 'X'
    O = 'O'
    
    SYMBOL_CHOICES = [
        (X, 'X'),
        (O, 'O'),
    ]
    
    ONGOING = 'ongoing'
    X_WINS = 'x_wins'
    O_WINS = 'o_wins'
    DRAW = 'draw'
    
    STATUS_CHOICES = [
        (ONGOING, 'Ongoing'),
        (X_WINS, 'X Wins'),
        (O_WINS, 'O Wins'),
        (DRAW, 'Draw'),
    ]
    
    room = models.OneToOneField(Room, on_delete=models.CASCADE)
    player_x = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_x')
    player_o = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_o')
    current_turn = models.CharField(max_length=1, choices=SYMBOL_CHOICES, default=X)
    board = models.JSONField(default=list)  # 3x3 поле как list of lists
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ONGOING)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='won_games')
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.board:
            self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Game in {self.room.name} - {self.status}"
    
    def check_winner(self):
        board = self.board
        
        #проверка по строкам
        for row in board:
            if row[0] == row[1] == row[2] != '':
                return row[0]
        
        #проверка по столбцам
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != '':
                return board[0][col]
        
        #проверка по диагоналям
        if board[0][0] == board[1][1] == board[2][2] != '':
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != '':
            return board[0][2]
        
        #ничья
        if all(cell != '' for row in board for cell in row):
            return 'draw'
        
        return None
    
    def make_move(self, row, col, player):
        if self.status != self.ONGOING:
            return False, "Игра на данный момент не идет"
        
        if self.board[row][col] != '':
            return False, "Клетка уже занята"
        
        #чекаем кто сейчас ходит
        if player == self.player_x:
            symbol = self.X
        elif player == self.player_o:
            symbol = self.O
        else:
            return False, "Игрока нет в игре"
        
        #чекаем если сейчас ход валидный
        if symbol != self.current_turn:
            return False, "Сейчас не твой ход!"
        
        #ходим
        self.board[row][col] = symbol
        
        #проверяем на победителя
        result = self.check_winner()
        if result == 'X':
            self.status = self.X_WINS
            self.winner = self.player_x
        elif result == 'O':
            self.status = self.O_WINS
            self.winner = self.player_o
        elif result == 'draw':
            self.status = self.DRAW
        else:
            #меняем очередь
            self.current_turn = self.O if self.current_turn == self.X else self.X
        
        self.save()
        return True, "Успешно сделан ход"