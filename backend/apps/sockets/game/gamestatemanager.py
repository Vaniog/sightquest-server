import dataclasses

from apps.api.serializers import GameSerializer
from apps.api.models import Game, Coordinate


class GameState:
    player_coordinates = {}

    def __init__(self, game: Game):
        self.game = game

    def set_player_coordinates(self, player_id: int, coordinates: Coordinate):
        self.player_coordinates[player_id] = coordinates

    def process_to_json(self):
        game_serializer = GameSerializer(self.game)
        for player in game_serializer.players:
            player.coordinates = 1


class GameStateManager:
    game_states = {}

    @staticmethod
    def get_game_state(code: str) -> GameState:
        game_state: GameState = GameStateManager.game_states.get(code, None)
        if game_state is None:
            game = Game.objects.filter(code=code).first()
            game_state = GameState(game)
            GameStateManager.game_states[code] = game_state
        return game_state

    @staticmethod
    def pop_game_state(code: str):
        GameStateManager.game_states.pop(code)
