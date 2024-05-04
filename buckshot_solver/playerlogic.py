import random

from buckshot_solver.elements import Action, Item, Shell
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

        items_dealer_set = set(cr.items_dealer) - {Item.adrenaline}

        if cr.saw_bonus == 2:
            possible_actions = possible_actions - {Action.saw}
            items_dealer_set = items_dealer_set - {Item.saw}
        if cr.dealer_handcuff:
            possible_actions = possible_actions - {Action.handcuff}
            items_dealer_set = items_dealer_set - {Item.handcuff}
        if len(items_dealer_set) == 0:
            possible_actions = possible_actions - {Action.adrenaline}

        actions: list[int] = []
        actions.append(random.choice(list(possible_actions)))
        proba = 1 / len(possible_actions)

        if actions[-1] == Action.adrenaline:
            actions.append(random.choice(list(items_dealer_set)))
            proba *= 1 / len(items_dealer_set)

        return proba, actions
