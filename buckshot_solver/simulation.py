import random

from buckshot_solver.elements import Item, Shell
from buckshot_solver.simulator import Round


class Simulation:
    def __init__(self, current_round: Round):
        self.c_round = current_round

    @property
    def _check(self) -> int:
        if self.c_round.player_life == 0:
            return -1
        if self.c_round.dealer_life == 0:
            return 1
        return 0

    @property
    def _bullets(self) -> int:
        return len(self.c_round.state)

    @property
    def _possible_actions(self) -> set[int]:
        if self.c_round.player_turn:
            return {i.value for i in self.c_round.items_player}.union({8, 9})
        return {i.value for i in self.c_round.items_dealer}.union({8, 9})

    def _one_random_item(self, items: list[Item]) -> Item:
        weights = [1] * 6
        if self.c_round.player_turn:
            items = self.c_round.items_player
        else:
            items = self.c_round.items_dealer
        if items.count(Item.cigarette) > 2:
            weights[Item.cigarette] = 0
        if items.count(Item.medecine) > 1:
            weights[Item.medecine] = 0
        if items.count(Item.adrenaline) > 2:
            weights[Item.adrenaline] = 0
        return random.choices(items, weights=weights)[0]

    def _generate_random_items(self) -> None:
        nb_items = random.randint(2, 5)
        nb_items_player = min(8 - len(self.c_round.items_player), nb_items)
        nb_items_dealer = min(8 - len(self.c_round.items_dealer), nb_items)
        for _ in range(nb_items_player):
            item = self._one_random_item(self.c_round.items_player)
            self.c_round.items_player.append(item)
        for _ in range(nb_items_dealer):
            item = self._one_random_item(self.c_round.items_dealer)
            self.c_round.items_dealer.append(item)

    def _random_next_round(self) -> None:
        nb_bullets = random.randint(2, 8)
        self.c_round.state = [Shell.unknown] * nb_bullets
        self.c_round.player_turn = True
        self.c_round.lives = nb_bullets // 2
        self.c_round.blanks = nb_bullets - self.c_round.lives
        self._generate_random_items()

    def start(self, first_action: int | None) -> int:
        if first_action is not None:
            if not self.c_round.action(first_action):
                return 0
        while self._check:
            if self._bullets:
                action: int = random.choice(list(self._possible_actions))
                self.c_round.action(action)
            else:
                self._random_next_round()

        return self._check
