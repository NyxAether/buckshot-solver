from buckshot_solver.elements import (Action, Item, RouletteResult, Shell,
                                      sum_res)
from buckshot_solver.logics.logic import Logic
from buckshot_solver.round import Round
from buckshot_solver.simulation import Simulation


class DealerLogicException(Exception):
    pass


class DealerLogic(Logic):

    def _choose_shoot(self, cr: Round) -> list[Action]:
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
            return [Action.opponent]
        if (
            next_blank
            or (next_live and cr.inverted)
            or remaining_blanks > remaining_lives
        ):
            return [Action.myself]
        # shell is unknown
        return [Action.opponent, Action.myself]

    def choose_actions(self, cr: Round) -> RouletteResult:
        if cr.player_turn:
            raise DealerLogicException(
                "Dealer was asked to choose an action but it was not its turn"
            )
        cr.update_both_knowledge()
        shells = cr.dealer_shells
        shoots_actions = self._choose_shoot(cr)

        items = cr.items_dealer.copy()
        if Item.adrenaline in cr.items_dealer:
            items.extend(cr.items_player)
        items_set = set(items)
        items_set = items_set - set([Item.adrenaline])
        # Allways remove saw because it will be use in shoot_opposite
        items_set.remove(Item.saw)

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

        results: list[RouletteResult] = []
        # If not item is left, shoot
        if len(items_set) == 0:
            for action in shoots_actions:
                cr_shot = cr.copy_round()
                results.append(self.action(cr_shot, action))
            return sum_res(results) / len(shoots_actions)

        # Choose next item
        outcomes = len(items_set)
        for item in items_set:
            cr_item = cr.copy_round()
            if item not in cr.items_dealer:
                cr_item.remove_played_item(Item.adrenaline)
                cr_item.items_player.remove(item)
                cr_item.items_dealer.append(item)
            results.append(self.action(cr_item, Action.from_item(item)))
        return sum_res(results) / outcomes

    def shoot_opposite(self, based_cr: Round) -> RouletteResult:
        cr = based_cr.copy_round()
        possible_actions = cr.possible_actions
        if Action.saw in possible_actions:
            cr.saw_bonus = 2
            cr.remove_played_item(Item.saw)
        elif (
            Action.adrenaline in possible_actions
            and Item.saw in cr.items_player
            and cr.saw_bonus == 1
        ):
            cr.items_player.remove(Item.saw)
            cr.saw_bonus = 2
            cr.remove_played_item(Item.adrenaline)
        last_shell = cr.remove_last_shell()
        if last_shell == Shell.live:
            if cr.player_turn:
                cr.dealer_life -= 1 * cr.saw_bonus
            else:
                cr.player_life -= 1 * cr.saw_bonus
            cr.lives -= 1
        else:
            cr.blanks -= 1
        cr.saw_bonus = 1
        cr.change_turn()
        return Simulation(cr).launch()
