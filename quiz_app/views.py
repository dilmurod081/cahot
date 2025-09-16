# quiz_app/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
from .models import Game, Player, Question, Choice, Answer

# Password for the Starter/Host
HOST_PASSWORD = '8877'


# Page-rendering Views
def home_view(request):
    """Renders the initial role selection and join/create page."""
    # Ensure the session key exists
    if not request.session.session_key:
        request.session.create()
    return render(request, 'quiz_app/home.html')


def game_view(request, game_code):
    """Renders the main game interface (lobby, quiz, results)."""
    game = get_object_or_404(Game, code=game_code)
    session_key = request.session.session_key

    # Determine if the current user is the host or a registered player
    is_host = game.host_session_key == session_key
    player = Player.objects.filter(game=game, session_key=session_key).first()

    context = {
        'game_code': game.code,
        'is_host': is_host,
        'player_id': player.id if player else None,
    }
    return render(request, 'quiz_app/game.html', context)


# API Views
@require_POST
def create_game_api(request):
    """API for the Starter to create a new game."""
    data = json.loads(request.body)
    password = data.get('password')

    if password != HOST_PASSWORD:
        return JsonResponse({'error': 'Incorrect password'}, status=403)

    if not request.session.session_key:
        request.session.create()

    game = Game.objects.create(host_session_key=request.session.session_key)
    return JsonResponse({'game_code': game.code})


@require_POST
def join_game_api(request):
    """API for players to join an existing game."""
    data = json.loads(request.body)
    game_code = data.get('game_code', '').upper()
    name = data.get('name', '').strip()

    if not all([game_code, name]):
        return JsonResponse({'error': 'Game code and name are required.'}, status=400)

    game = Game.objects.filter(code=game_code, status='joining').first()
    if not game:
        return JsonResponse({'error': 'Game not found or has already started.'}, status=404)

    if not request.session.session_key:
        request.session.create()

    player, created = Player.objects.update_or_create(
        game=game,
        session_key=request.session.session_key,
        defaults={'name': name}
    )
    return JsonResponse({'game_code': game.code})


def game_state_api(request, game_code):
    """The core API that provides real-time state to all clients."""
    game = get_object_or_404(Game, code=game_code)
    players = Player.objects.filter(game=game).order_by('name')

    state = {
        'status': game.status,
        'players': [{'id': p.id, 'name': p.name, 'score': p.score} for p in players],
    }

    if game.status == 'in-progress':
        question = game.current_question
        answered_player_ids = Answer.objects.filter(question=question).values_list('player_id', flat=True)

        state['question'] = {
            'id': question.id,
            'text': question.text,
            'choices': [choice.text for choice in question.choices.all()],
            'time_left': round(
                (game.question_start_time + timezone.timedelta(seconds=15) - timezone.now()).total_seconds()),
        }
        state['answered_player_ids'] = list(answered_player_ids)

    return JsonResponse(state)


@require_POST
def submit_answer_api(request, game_code):
    """API for a player to submit their answer."""
    game = get_object_or_404(Game, code=game_code, status='in-progress')
    player = get_object_or_404(Player, game=game, session_key=request.session.session_key)

    # Prevent answering twice
    if Answer.objects.filter(player=player, question=game.current_question).exists():
        return JsonResponse({'error': 'Already answered'}, status=400)

    Answer.objects.create(player=player, question=game.current_question)
    return JsonResponse({'status': 'ok'})


# Host-specific API Views
@require_POST
def start_game_api(request, game_code):
    """API for the host to start the game and move to the first question."""
    game = get_object_or_404(Game, code=game_code, host_session_key=request.session.session_key)

    first_question = Question.objects.order_by('?').first()
    if not first_question:
        return JsonResponse({'error': 'No questions found in the database.'}, status=400)

    game.status = 'in-progress'
    game.current_question = first_question
    game.question_start_time = timezone.now()
    game.save()

    return JsonResponse({'status': 'game started'})


@require_POST
def delete_player_api(request, game_code):
    """API for the host to remove a player from the lobby."""
    game = get_object_or_404(Game, code=game_code, host_session_key=request.session.session_key)
    data = json.loads(request.body)
    player_id = data.get('player_id')

    player_to_delete = get_object_or_404(Player, id=player_id, game=game)
    # Host cannot delete themselves
    if player_to_delete.session_key != game.host_session_key:
        player_to_delete.delete()

    return JsonResponse({'status': 'player deleted'})