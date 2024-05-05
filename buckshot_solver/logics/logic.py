from abc import ABC, abstractmethod

from buckshot_solver.elements import (Action, Item, RouletteResult, Shell,
                                      sum_res)
from buckshot_solver.round import Round
from buckshot_solver.simulation import Simulation, SimulationError


class Logic(ABC):
    @abstractmethod
    def choose_actions(self, cr: Round) -> RouletteResult:
        pass

    def action(self, cr: Round, action: Action | int) -> RouletteResult:
        match action:
            case Action.handcuff:
                return self.handcuff(cr)
            case Action.magnifier:
                return self.magnifier(cr)
            case Action.saw:
                return self.saw(cr)
            case Action.phone:
                return self.phone(cr)
            case Action.beer:
                return self.beer(cr)
            case Action.cigarette:
                return self.cigarette(cr)
            case Action.medecine:
                return self.medecine(cr)
            case Action.inverter:
                return self.inverter(cr)
            case Action.adrenaline:
                return self.adrenaline(cr)
            case Action.opponent:
                return self.shoot_opposite(cr)
            case Action.myself:
                return self.shoot_myself(cr)
        raise SimulationError(f"Unknown action: {action}")

    def handcuff(self, based_cr: Round) -> RouletteResult:
        cr = based_cr.copy_round()
        if cr.player_turn:
            cr.dealer_handcuff = True
        else:
            cr.player_handcuff = True
        cr.remove_played_item(Item.handcuff)
        return Simulation(cr).launch()

    def magnifier(self, based_cr: Round) -> RouletteResult:
        cr = based_cr.copy_round()
        if cr.player_turn:
            cr.player_shells[-1] = cr.shells[-1]
        else:
            cr.dealer_shells[-1] = cr.shells[-1]
        cr.update_both_knowledge()
        cr.remove_played_item(Item.magnifier)
        return Simulation(cr).launch()

    def saw(self, based_cr: Round) -> RouletteResult:
        cr = based_cr.copy_round()
        if cr.saw_bonus == 1:
            cr.saw_bonus = 2
            cr.remove_played_item(Item.saw)
        return Simulation(cr).launch()

    def phone(self, based_cr: Round) -> RouletteResult:
        outcomes = len(based_cr.shells) - 1
        results: list[RouletteResult] = []
        for i in range(outcomes):
            cr = based_cr.copy_round()
            if cr.player_turn:
                cr.player_shells[i] = cr.shells[i]
            else:
                cr.dealer_shells[i] = cr.shells[i]
            cr.update_both_knowledge()
            cr.remove_played_item(Item.phone)
            results.append(Simulation(cr).launch())
        res = sum_res(results) / outcomes
        return res

    def beer(self, based_cr: Round) -> RouletteResult:
        cr = based_cr.copy_round()
        last_shell = cr.remove_last_shell()
        if last_shell == Shell.live:
            cr.lives -= 1
        elif last_shell == Shell.blank:
            cr.blanks -= 1
        cr.remove_played_item(Item.beer)
        return Simulation(cr).launch()

    def cigarette(self, based_cr: Round) -> RouletteResult:
        cr = based_cr.copy_round()
        if cr.player_turn and cr.player_life < cr.max_life:
            cr.player_life += 1
        if not cr.player_turn and cr.dealer_life < cr.max_life:
            cr.dealer_life += 1
        cr.remove_played_item(Item.cigarette)
        return Simulation(cr).launch()

    def medecine(self, based_cr: Round) -> RouletteResult:
        outcomes = 2
        heals = [0, 1]
        results = []
        for heal in heals:
            cr = based_cr.copy_round()
            if heal == 0:
                if cr.player_turn:
                    cr.player_life -= 1
                else:
                    cr.dealer_life -= 1
            else:
                if cr.player_turn and cr.player_life < cr.max_life:
                    cr.player_life += 1
                if not cr.player_turn and cr.dealer_life < cr.max_life:
                    cr.dealer_life += 1
            cr.remove_played_item(Item.medecine)
            results.append(Simulation(cr).launch())
        return sum_res(results) / outcomes

    def inverter(self, based_cr: Round) -> RouletteResult:
        cr = based_cr.copy_round()
        cr.inverted = not cr.inverted
        cr.remove_played_item(Item.inverter)
        return Simulation(cr).launch()

    def adrenaline(self, based_cr: Round) -> RouletteResult:
        cr_copy = based_cr.copy_round()
        cr_copy.adrenaline = True
        set_items = set(
            cr_copy.items_player if cr_copy.player_turn else cr_copy.items_dealer
        )
        results = []
        outcomes = len(cr_copy.possible_actions)
        for item in set_items:
            cr = cr_copy.copy_round()
            cr.remove_played_item(Item.adrenaline)
            if cr.player_turn:
                cr.items_player.append(item)
                cr.items_dealer.remove(item)
            else:
                cr.items_player.remove(item)
                cr.items_dealer.append(item)
            results.append(Simulation(cr).launch())
        if based_cr.player_turn:
            return max(results)
        return sum_res(results) / outcomes

    def shoot_opposite(self, based_cr: Round) -> RouletteResult:
        cr = based_cr.copy_round()
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

    def shoot_myself(self, based_cr: Round) -> RouletteResult:
        cr = based_cr.copy_round()
        last_shell = cr.remove_last_shell()
        if last_shell == Shell.live:
            if cr.player_turn:
                cr.player_life -= 1 * cr.saw_bonus
            else:
                cr.dealer_life -= 1 * cr.saw_bonus
            cr.lives -= 1
            cr.change_turn()
        else:
            cr.blanks -= 1
        cr.saw_bonus = 1
        return Simulation(cr).launch()
