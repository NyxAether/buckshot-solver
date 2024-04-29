import random
from functools import wraps
from typing import Any, Callable

from pydantic import BaseModel

from buckshot_solver.elements import Action, Item, Shell


def check_item(item: Item) -> Callable:
    def wrapper_up(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self: "Round", *args: Any, **kwargs: Any) -> Any:
            if self.player_turn:
                if item in self.items_player:
                    return func(self, *args, **kwargs)
            else:
                if item in self.items_dealer:
                    return func(self, *args, **kwargs)
            return False

        return wrapper

    return wrapper_up


class Round(BaseModel):
    lives: int
    blanks: int
    player_life: int
    dealer_life: int
    max_life: int
    player_turn: bool = True
    player_handcuff: bool = False
    dealer_handcuff: bool = False
    saw_bonus: int = 1
    items_player: list[Item] = []
    items_dealer: list[Item] = []
    shells: list[Shell] = []
    player_shells: list[Shell] = []
    dealer_shells: list[Shell] = []

    def model_post_init(self, __context: Any) -> None:
        if self.shells == []:
            self.shells = [Shell.unknown] * (self.lives + self.blanks)
        if self.player_shells == []:
            self.player_shells = [Shell.unknown] * (self.lives + self.blanks)
        if self.dealer_shells == []:
            self.dealer_shells = [Shell.unknown] * (self.lives + self.blanks)

    @classmethod
    def from_round(cls, el: "Round") -> "Round":
        values = el.model_dump()
        values["items_player"] = el.items_player.copy()
        values["items_dealer"] = el.items_dealer.copy()
        if el.shells is not None:
            values["shells"] = el.shells.copy()
            values["player_shells"] = el.player_shells.copy()
            values["dealer_shells"] = el.dealer_shells.copy()
        return Round(**values)

    @property
    def check_health(self) -> bool:
        if self.player_life < 0:
            self.player_life = 0
        if self.dealer_life < 0:
            self.dealer_life = 0
        return self.player_life != 0 and self.dealer_life != 0

    @property
    def bullets(self) -> int:
        return len(self.shells)

    def _check_adrenaline(self) -> bool:
        nb_item_dealer = len(self.items_dealer) - self.items_dealer.count(
            Item.adrenaline
        )
        nb_item_player = len(self.items_player) - self.items_player.count(
            Item.adrenaline
        )
        if self.player_turn and nb_item_dealer > 0:
            return True
        if not self.player_turn and nb_item_player > 0:
            return True
        return False

    def _remove_played_item(self, item: Item) -> None:
        if self.player_turn:
            self.items_player.remove(item)
        else:
            self.items_dealer.remove(item)

    def _remove_last_shell(self) -> None:
        del self.shells[-1]
        del self.player_shells[-1]
        del self.dealer_shells[-1]

    @check_item(item=Item.handcuff)
    def ac_handcuff(self) -> float:
        if self.player_turn and not self.dealer_handcuff:
            self.dealer_handcuff = True
            self._remove_played_item(Item.handcuff)
            return 1.0
        if not self.player_turn and not self.player_handcuff:
            self.player_handcuff = True
            self._remove_played_item(Item.handcuff)
            return 1.0
        return 0.0

    @check_item(item=Item.magnifier)
    def ac_magnifier(self) -> float:
        proba = 1.0
        if self.player_turn:
            self.player_shells[-1] = self.shells[-1]
        else:
            self.dealer_shells[-1] = self.shells[-1]
        self._remove_played_item(Item.magnifier)
        return proba

    @check_item(item=Item.saw)
    def ac_saw(self) -> float:
        if self.saw_bonus == 1:
            self.saw_bonus = 2
            self._remove_played_item(Item.saw)
            return 1.0
        return 0.0

    @check_item(item=Item.phone)
    def ac_phone(self) -> float:
        if len(self.shells) > 1:
            id_shell = random.randint(0, len(self.shells) - 1)
            proba = 1 / (len(self.shells) - 1)
            if self.player_turn:
                self.player_shells[id_shell] = self.shells[id_shell]
            else:
                self.dealer_shells[id_shell] = self.shells[id_shell]
            self._remove_played_item(Item.phone)
            return proba
        return 0.0

    @check_item(item=Item.beer)
    def ac_beer(self) -> float:
        proba = 1.0
        if self.shells[-1] == Shell.live:
            self.lives -= 1
        elif self.shells[-1] == Shell.blank:
            self.blanks -= 1
        self._remove_last_shell()
        self._remove_played_item(Item.beer)
        return proba

    @check_item(item=Item.cigarette)
    def ac_cigarette(self) -> float:
        if self.player_turn and self.player_life < self.max_life:
            self.player_life += 1
        if not self.player_turn and self.dealer_life < self.max_life:
            self.dealer_life += 1
        self._remove_played_item(Item.cigarette)
        return 1.0

    @check_item(item=Item.medecine)
    def ac_medecine(self) -> float:
        heal = random.randint(0, 1)
        if heal == 0:
            if self.player_turn:
                self.player_life -= 1
            else:
                self.dealer_life -= 1
        else:
            if self.player_turn and self.player_life < self.max_life:
                self.player_life += 1
            if not self.player_turn and self.dealer_life < self.max_life:
                self.dealer_life += 1
        self._remove_played_item(Item.medecine)
        return 0.5

    @check_item(item=Item.adrenaline)
    def ac_adrenaline(self) -> float:
        if self._check_adrenaline():
            proba = 1.0
            if self.player_turn:
                items_no_ad = {i for i in self.items_dealer if i != Item.adrenaline}
                item = random.choice(list(items_no_ad))
                self.items_player.append(item)
                self.items_dealer.remove(item)
            else:
                items_no_ad = {i for i in self.items_player if i != Item.adrenaline}
                item = random.choice(list(items_no_ad))
                proba = proba * 1 / len(items_no_ad)
                self.items_dealer.append(item)
                self.items_player.remove(item)
            self._remove_played_item(Item.adrenaline)
            return proba
        return 0.0

    def ac_shoot_opposite(self) -> float:
        if self.shells[-1] == Shell.live:
            if self.player_turn:
                self.dealer_life -= 1 * self.saw_bonus
            else:
                self.player_life -= 1 * self.saw_bonus
            self.lives -= 1
        else:
            self.blanks -= 1
        self.saw_bonus = 1
        self.change_turn()
        self._remove_last_shell()
        return 1.0

    def ac_shoot_myself(self) -> float:
        if self.shells[-1] == Shell.live:
            if self.player_turn:
                self.player_life -= 1 * self.saw_bonus
            else:
                self.dealer_life -= 1 * self.saw_bonus
            self.lives -= 1
            self.change_turn()
        else:
            self.blanks -= 1
        self.saw_bonus = 1
        self._remove_last_shell()
        return 1.0

    def change_turn(self) -> None:
        if self.player_turn:
            if self.dealer_handcuff:
                self.dealer_handcuff = False
            else:
                self.player_turn = False
        else:
            if self.player_handcuff:
                self.player_handcuff = False
            else:
                self.player_turn = True

    @property
    def possible_actions(self) -> set[int]:
        possible_shots = {Action.opponent.value, Action.myself.value}
        if self.player_turn:
            return {i.value for i in self.items_player}.union(possible_shots)
        return {i.value for i in self.items_dealer}.union(possible_shots)

    def action(self, action: int) -> float:
        match action:
            case 0:
                return self.ac_handcuff()
            case 1:
                return self.ac_magnifier()
            case 2:
                return self.ac_saw()
            case 3:
                return self.ac_phone()
            case 4:
                return self.ac_beer()
            case 5:
                return self.ac_cigarette()
            case 6:
                return self.ac_medecine()
            case 7:
                return self.ac_adrenaline()
            case 8:
                return self.ac_shoot_opposite()
            case 9:
                return self.ac_shoot_myself()
        return 0.0

    def initialize_shells(self) -> None:
        remaining_lives = self.lives - self.player_shells.count(Shell.live)
        remaining_blanks = self.blanks - self.player_shells.count(Shell.blank)
        for i, shell in enumerate(self.shells):
            if shell == Shell.unknown:
                self.shells[i] = random.choices(
                    [Shell.live, Shell.blank], [remaining_lives, remaining_blanks]
                )[0]
                if self.shells[i] == Shell.live:
                    remaining_lives -= 1
                else:
                    remaining_blanks -= 1
