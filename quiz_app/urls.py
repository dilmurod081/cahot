# quiz_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('game/<str:game_code>/', views.game_view, name='game'),

    # API endpoints for real-time updates
    path('api/create_game/', views.create_game_api, name='create_game_api'),
    path('api/join_game/', views.join_game_api, name='join_game_api'),
    path('api/game_state/<str:game_code>/', views.game_state_api, name='game_state_api'),
    path('api/submit_answer/<str:game_code>/', views.submit_answer_api, name='submit_answer_api'),

    # API endpoints for the Starter/Host
    path('api/host/start_game/<str:game_code>/', views.start_game_api, name='start_game_api'),
    path('api/host/delete_player/<str:game_code>/', views.delete_player_api, name='delete_player_api'),
]