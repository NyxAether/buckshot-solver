import random

from buckshot_solver.elements import Action, Item, Shell
from buckshot_solver.round import Round


class DealerLogicException(Exception):
    pass


class DealerLogic:

    def _choose_shoot(self, c_round: Round) -> tuple[float, Action]:
        shells = c_round.dealer_shells
        if shells[-1] == Shell.live:
            return 1.0, Action.opponent
        if shells[-1] == Shell.blank:
            return 1.0, Action.myself
        # shell is unknown
        remain_lives = c_round.lives - c_round.dealer_shells.count(Shell.live)
        remain_blanks = c_round.blanks - c_round.dealer_shells.count(Shell.blank)
        if remain_lives > remain_blanks:
            return 1.0, Action.opponent
        if remain_blanks > remain_lives:
            return 1.0, Action.myself
        # if remain_blanks == remain_lives
        return 0.5, random.choice([Action.opponent, Action.myself])

    def choose_actions(self, c_round: Round) -> tuple[float, list[int]]:
        proba = 1.0
        shells = c_round.dealer_shells
        p_if_shoot, if_shoot = self._choose_shoot(c_round)
        if c_round.player_turn:
            raise DealerLogicException(
                "Dealer was asked to choose an action but it was not its turn"
            )
        if len(c_round.items_dealer) == 0:
            return proba * p_if_shoot, [if_shoot]

        items = c_round.items_dealer.copy()
        if Item.adrenaline in c_round.items_dealer:
            items.extend(c_round.items_player)
        items_set = set(items)
        items_set = items_set - set([Item.adrenaline])
        if Item.handcuff in items_set:
            if c_round.player_handcuff or len(shells) < 2:
                items_set.remove(Item.handcuff)
        if Item.magnifier in items_set:
            if shells[-1] != Shell.unknown:
                items_set.remove(Item.magnifier)
        if Item.phone in items_set:
            if len(shells) <= 2 or shells.count(Shell.unknown) == 0:
                items_set.remove(Item.phone)
        if Item.beer in items_set:
            if len(shells) <= 1 or shells[-1] == Shell.live:
                items_set.remove(Item.beer)
        if Item.cigarette in items_set:
            if c_round.dealer_life == c_round.max_life:
                items_set.remove(Item.cigarette)
        if Item.medecine in items_set:
            if (
                Item.cigarette in items_set
                or c_round.dealer_life == c_round.max_life
                or c_round.dealer_life == 1
            ):
                items_set.remove(Item.medecine)
        if Item.saw in items_set:
            if (
                shells[-1] == Shell.blank
                or items_set != set([Item.saw])
                or c_round.saw_bonus == 2
                or if_shoot == Action.myself
            ):
                items_set.remove(Item.saw)

        if len(items_set) == 0:
            return proba * p_if_shoot, [if_shoot]
        next_item: Item = random.choice(list(items_set))
        proba = 1.0 / len(items_set)
        actions_list: list[int] = []
        if next_item not in c_round.items_dealer:
            actions_list.append(Item.adrenaline)
        actions_list.append(next_item)
        if next_item == Item.saw:
            actions_list.append(if_shoot)
            proba = proba * p_if_shoot
        return proba, actions_list
