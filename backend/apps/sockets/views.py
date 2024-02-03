from django.shortcuts import render


def game_socket(request):
    return render(request, "game.html")
