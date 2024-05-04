import random

from buckshot_solver.dealerlogic import DealerLogic
from buckshot_solver.elements import Action, Item, Shell
from buckshot_solver.playerlogic import PlayerLogic
from buckshot_solver.round import Round


class SimulationError(Exception):
    pass


class Simulation:
    def __init__(self, current_round: Round):
        self.cr = current_round
        self.cr.initialize_shells()
        self.dealer = DealerLogic()
        self.player = PlayerLogic()

    def _one_random_item(self, items: list[Item]) -> Item:
        weights = [1] * 6
        if self.cr.player_turn:
            items = self.cr.items_player
        else:
            items = self.cr.items_dealer
        if items.count(Item.cigarette) > 2:
            weights[Item.cigarette] = 0
        if items.count(Item.medecine) > 1:
            weights[Item.medecine] = 0
        if items.count(Item.adrenaline) > 2:
            weights[Item.adrenaline] = 0
        return random.choices(items, weights=weights)[0]

    def _generate_random_items(self) -> None:
        nb_items = random.randint(2, 5)
        nb_items_player = min(8 - len(self.cr.items_player), nb_items)
        nb_items_dealer = min(8 - len(self.cr.items_dealer), nb_items)
        for _ in range(nb_items_player):
            item = self._one_random_item(self.cr.items_player)
            self.cr.items_player.append(item)
        for _ in range(nb_items_dealer):
            item = self._one_random_item(self.cr.items_dealer)
            self.cr.items_dealer.append(item)

    def _random_next_round(self) -> None:
        nb_bullets = random.randint(2, 8)
        self.cr.shells = [Shell.unknown] * nb_bullets
        self.cr.player_turn = True
        self.cr.lives = nb_bullets // 2
        self.cr.blanks = nb_bullets - self.cr.lives
        self._generate_random_items()

    def start(
        self, first_action: Action | int | None = None, extended: bool = False
    ) -> int:
        action_count = 0
        if first_action is not None:
            action_count += 1
            if self.cr.action(first_action) == 0.0:
                raise SimulationError(
                    f"First action {Action.int_to_str(first_action)} not possible"
                )
        while self.cr.check_health:
            if self.cr.bullets:
                if self.cr.player_turn:
                    _, actions = self.player.choose_actions(self.cr)
                    # proba *= p_action
                else:
                    _, actions = self.dealer.choose_actions(self.cr)
                action_count += len(actions)
                for action in actions:
                    _ = self.cr.action(action)
            elif extended:
                self._random_next_round()
            else:
                break
        return action_count
