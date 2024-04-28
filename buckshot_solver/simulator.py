from buckshot_solver.elements import Item, Shell
from buckshot_solver.round import Round


class Simulator:
    def __init__(
        self,
        lives: int,
        blanks: int,
        max_life: int,
        items_player: list[Item],
        items_dealer: list[Item],
        player_turn: bool = True,
        nb_simulations: int = 10_000,
    ):
        self.freezed_round = Round(
            lives=lives,
            blanks=blanks,
            max_life=max_life,
            player_life=max_life,
            dealer_life=max_life,
            items_player=items_player,
            items_dealer=items_dealer,
            player_turn=player_turn,
            state=[Shell.unknown] * (lives + blanks),
        )
        self.nb_simulations = nb_simulations

    def start(self) -> None:
        for _ in range(self.nb_simulations):
            current_round = self.freezed_round.from_round(self.freezed_round)
            # each index corresponds to the corresponding item
            # index 7: shoot opposite, index 8: shoot self
            nb_wins = [0] * 8
