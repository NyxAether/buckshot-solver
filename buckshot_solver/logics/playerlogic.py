from buckshot_solver.elements import Action, RouletteResult
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

    def first_choose_actions(self, cr: Round) -> dict[Action, RouletteResult]:
        if not cr.player_turn:
            raise PlayerLogicException(
                "Player was asked to choose an action but it was not its turn"
            )
        cr.update_both_knowledge()
        possible_actions = cr.possible_actions
        results: dict[Action, RouletteResult] = {
            action: self.action(cr, action) for action in possible_actions
        }
        return results
