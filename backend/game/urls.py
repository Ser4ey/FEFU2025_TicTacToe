from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from . import views

@ensure_csrf_cookie
def csrf_token_view(request):
    from django.http import JsonResponse
    return JsonResponse({'csrfToken': 'success'})

urlpatterns = [
    #csrf токен
    path('csrf/', csrf_token_view, name='csrf_token'),
    
    #аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.current_user, name='current_user'),
    path('stats/', views.user_stats, name='user_stats'),
    
    #комнаты: список, создание, вход/выход, быстрый матч
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.create_room, name='create_room'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/<int:room_id>/join/', views.join_room, name='join_room'),
    path('rooms/<int:room_id>/leave/', views.leave_room, name='leave_room'),
    path('quick-game/', views.quick_game, name='quick_game'),
    
    #игровой ход
    path('rooms/<int:room_id>/move/', views.make_move, name='make_move'),
]