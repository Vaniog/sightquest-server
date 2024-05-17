from django.shortcuts import render


def game_socket(request):
    return render(request, "game.html")


def game_v2(request):
    return render(request, "game_v2.html")
