from django.shortcuts import render


def lobby(request):
    return render(request, "chat/chat.html")


def game_socket(request):
    return render(request, "game.html")


def lobby_socket(request):
    return render(request, "lobby.html")
