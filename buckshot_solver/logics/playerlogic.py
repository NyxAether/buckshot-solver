from buckshot_solver.elements import RouletteResult
from buckshot_solver.logics.logic import Logic
from buckshot_solver.round import Round


class PlayerLogicException(Exception):
    pass


class PlayerLogic(Logic):
    def choose_actions(self, cr: Round) -> RouletteResult:
        if not cr.player_turn:
            raise PlayerLogicException(
                "Player was asked to choose an action but it was not its turn"
            )
        cr.update_both_knowledge()
        possible_actions = cr.possible_actions
        results: list[RouletteResult] = [
            self.action(cr, action) for action in possible_actions
        ]
        return max(results)
