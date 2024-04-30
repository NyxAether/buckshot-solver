import random

from buckshot_solver.elements import Action, Shell
from buckshot_solver.round import Round


class PlayerLogicException(Exception):
    pass


class PlayerLogic:
    def choose_actions(self, cr: Round) -> tuple[float, list[int]]:
        if not cr.player_turn:
            raise PlayerLogicException(
                "Player was asked to choose an action but it was not its turn"
            )
        cr.update_both_knowledge()
        possible_actions = cr.possible_actions
        inverted = cr.inverted
        next_live = cr.player_shells[-1] == Shell.live
        next_blank = cr.player_shells[-1] == Shell.blank
        # Next shell is live
        if (next_live and not inverted) or (next_blank and inverted):
            possible_actions = possible_actions - {Action.myself}
        # Next shell is blank
        if (next_blank and not inverted) or (next_live and inverted):
            possible_actions = possible_actions - {Action.opponent}
        action: int = random.choice(list(possible_actions))
        proba = 1 / len(possible_actions)
        return proba, [action]
