from buckshot_solver.elements import RouletteResult
from buckshot_solver.logics.dealerlogic import DealerLogic
from buckshot_solver.logics.playerlogic import PlayerLogic
from buckshot_solver.round import Round


class SimulationError(Exception):
    pass


class Simulation:
    def __init__(self, current_round: Round):
        self.cr = current_round
        self.dealer = DealerLogic()
        self.player = PlayerLogic()

    def launch(self) -> RouletteResult:
        if self.cr.check_health and self.cr.bullets:
            if self.cr.player_turn:
                return self.player.choose_actions(self.cr)
            else:
                return self.dealer.choose_actions(self.cr)
        return RouletteResult(
            player_life=self.cr.player_life, dealer_life=self.cr.dealer_life
        )
