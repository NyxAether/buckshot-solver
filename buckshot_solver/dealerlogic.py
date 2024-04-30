import random

from buckshot_solver.elements import Action, Item, Shell
from buckshot_solver.round import Round


class DealerLogicException(Exception):
    pass


class DealerLogic:

    def _choose_shoot(self, cr: Round) -> tuple[float, Action]:
        shells = cr.dealer_shells
        next_live = shells[-1] == Shell.live
        next_blank = shells[-1] == Shell.blank
        remaining_lives = cr.lives - cr.dealer_shells.count(Shell.live)
        remaining_blanks = cr.blanks - cr.dealer_shells.count(Shell.blank)
        if (
            next_live
            or (next_blank and cr.inverted)
            or remaining_lives > remaining_blanks
        ):
            return 1.0, Action.opponent
        if (
            next_blank
            or (next_live and cr.inverted)
            or remaining_blanks > remaining_lives
        ):
            return 1.0, Action.myself
        # shell is unknown
        return 0.5, random.choice([Action.opponent, Action.myself])

    def choose_actions(self, cr: Round) -> tuple[float, list[int]]:
        if cr.player_turn:
            raise DealerLogicException(
                "Dealer was asked to choose an action but it was not its turn"
            )
        proba = 1.0
        cr.update_both_knowledge()
        shells = cr.dealer_shells
        p_if_shoot, if_shoot = self._choose_shoot(cr)
        if len(cr.items_dealer) == 0:
            return proba * p_if_shoot, [if_shoot]

        items = cr.items_dealer.copy()
        if Item.adrenaline in cr.items_dealer:
            items.extend(cr.items_player)
        items_set = set(items)
        items_set = items_set - set([Item.adrenaline])

        # Remove items that the dealer will not choose
        if Item.handcuff in items_set:
            if cr.player_handcuff or len(shells) < 2:
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
            if cr.dealer_life == cr.max_life:
                items_set.remove(Item.cigarette)
        if Item.medecine in items_set:
            if (
                Item.cigarette in items_set
                or cr.dealer_life == cr.max_life
                or cr.dealer_life == 1
            ):
                items_set.remove(Item.medecine)
        if Item.inverter in items_set:
            if cr.inverted or shells[-1] != Shell.blank:
                items_set.remove(Item.inverter)
        if Item.saw in items_set:
            if (
                shells[-1] == Shell.blank
                or items_set != set([Item.saw])
                or cr.saw_bonus == 2
                or if_shoot == Action.myself
            ):
                items_set.remove(Item.saw)

        # If not item is left, shoot§
        if len(items_set) == 0:
            return proba * p_if_shoot, [if_shoot]

        # Choose next item randomly
        next_item: Item = random.choice(list(items_set))
        proba = 1.0 / len(items_set)
        actions_list: list[int] = []
        if next_item not in cr.items_dealer:
            actions_list.append(Item.adrenaline)
        actions_list.append(next_item)
        if next_item == Item.saw:
            actions_list.append(if_shoot)
            proba = proba * p_if_shoot
        return proba, actions_list
