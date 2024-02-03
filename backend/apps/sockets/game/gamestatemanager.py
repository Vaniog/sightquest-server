from apps.api.serializers import GameSerializer
from apps.api.models import Game, Coordinate, GameUser


class GameState:
    player_coordinates = {}

    def __init__(self, game: Game):
        self.game = game
        self.game_json = GameSerializer(game).data

    def update_from_db(self):
        self.game_json = GameSerializer(self.game).data

    def set_player_coordinates(self, player_id: int, coordinates: Coordinate):
        self.player_coordinates[player_id] = coordinates

    def process_to_json(self):
        for player in self.game_json["players"]:
            player["coordinates"] = self.player_coordinates.get(player["user"]["id"], None) \
                                    or {"latitude": 0, "longitude": 0}
        return self.game_json

    def add_player(self, user):
        GameUser(user=user, game=self.game).save()
        self.update_from_db()


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
