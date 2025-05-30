# Крестики-нолики (Tic Tac Toe)

Многопользовательская игра "Крестики-нолики" с веб-интерфейсом.

## Технологии

- **Backend**: Python + Django + Django REST Framework
- **Frontend**: React + JavaScript
- **База данных**: SQLite
- **API**: REST API

## Функциональность

### Основные возможности:
1. **Регистрация и авторизация** - пользователи должны войти в систему перед игрой
2. **Система комнат** - игроки создают комнаты или присоединяются к существующим
3. **Быстрая игра** - автоматический поиск доступной комнаты или создание новой
4. **Статистика** - отслеживание побед, поражений и ничьих для каждого игрока

### Страницы:
- Страница входа и регистрации
- Главная страница с навигацией
- Список комнат
- Игровая комната
- Статистика игрока

## Установка и запуск

### Требования
- Python 3.8+
- Node.js 14+
- npm или yarn

### Backend (Django)
1. Перейдите в папку backend:
```bash
cd backend
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# или
source venv/bin/activate  # Linux/Mac
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Выполните миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Создайте суперпользователя (опционально):
```bash
python manage.py createsuperuser
```

6. Запустите сервер:
```bash
python manage.py runserver
```

Backend будет доступен по адресу: http://localhost:8000

### Frontend (React)

1. Перейдите в папку frontend:
```bash
cd frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите приложение:
```bash
npm start
```

Frontend будет доступен по адресу: http://localhost:3000

## API Endpoints

### Аутентификация
- `POST /api/register/` - Регистрация
- `POST /api/login/` - Вход
- `POST /api/logout/` - Выход
- `GET /api/user/` - Текущий пользователь
- `GET /api/stats/` - Статистика пользователя

### Комнаты
- `GET /api/rooms/` - Список комнат
- `POST /api/rooms/create/` - Создать комнату
- `GET /api/rooms/{id}/` - Детали комнаты
- `POST /api/rooms/{id}/join/` - Присоединиться к комнате
- `POST /api/rooms/{id}/leave/` - Покинуть комнату
- `POST /api/quick-game/` - Быстрая игра

### Игра
- `POST /api/rooms/{id}/move/` - Сделать ход

## Структура проекта

```
ttac/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── tictactoe/          # Настройки Django
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── game/               # Django приложение
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
└── frontend/               # React приложение
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── App.js
        ├── App.css
        ├── index.js
        └── components/
            ├── Login.js
            ├── Register.js
            ├── Home.js
            ├── RoomList.js
            ├── GameRoom.js
            └── Stats.js
```

## Модели данных

### UserProfile
- Расширение стандартной модели User
- Хранит статистику игр (побед, поражений, ничьих)

### Room
- Игровая комната
- Содержит название, код, создателя, игроков и статус

### Game
- Игровая сессия
- Связана с комнатой, содержит игроков, доску и текущее состояние

## Особенности реализации

1. **Простота** - минимальные зависимости, простая архитектура
2. **REST API** - полное разделение frontend и backend
3. **Автоматическое обновление** - периодическое обновление состояния игры
4. **Адаптивный дизайн** - работает на мобильных устройствах
5. **Валидация ходов** - проверка корректности ходов на backend

## Разработка

Для разработки рекомендуется запускать backend и frontend одновременно в разных терминалах.

Backend (порт 8000):
```bash
cd backend
python manage.py runserver
```

Frontend (порт 3000):
```bash
cd frontend
npm start
```

## Админ панель

Доступна по адресу: http://localhost:8000/admin/

Позволяет управлять пользователями, комнатами и играми.