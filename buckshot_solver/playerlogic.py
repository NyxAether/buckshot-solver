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
        possible_actions = cr.possible_actions
        remaining_lives = cr.lives - cr.player_shells.count(Shell.live)
        remaining_blanks = cr.blanks - cr.player_shells.count(Shell.blank)
        # Next shell is live
        if cr.player_shells[-1] == Shell.live:
            possible_actions = possible_actions - {Action.myself}
        if cr.player_shells[-1] == Shell.unknown and remaining_blanks == 0:
            possible_actions = possible_actions - {Action.myself}
        # Next shell is blank
        if cr.player_shells[-1] == Shell.blank:
            possible_actions = possible_actions - {Action.opponent}
        if cr.player_shells[-1] == Shell.unknown and remaining_lives == 0:
            possible_actions = possible_actions - {Action.opponent}
        action: int = random.choice(list(possible_actions))
        proba = 1 / len(possible_actions)
        return proba, [action]
