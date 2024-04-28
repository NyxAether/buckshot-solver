import random
from functools import wraps
from typing import Any, Callable

from pydantic import BaseModel

from buckshot_solver.elements import Item, Shell


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
    items_player: list[Item]
    items_dealer: list[Item]
    lives: int
    blanks: int
    player_life: int
    dealer_life: int
    max_life: int
    player_turn: bool = True
    player_handcuff: bool = False
    dealer_handcuff: bool = False
    saw_bonus: int = 1
    state: list[Shell] = []

    def model_post_init(self, __context: Any) -> None:
        self.state = [Shell.unknown] * (self.lives + self.blanks)

    @classmethod
    def from_round(cls, el: "Round") -> "Round":
        values = el.model_dump()
        values["items_player"] = el.items_player.copy()
        values["items_dealer"] = el.items_dealer.copy()
        if el.state is not None:
            values["state"] = el.state.copy()
        return Round(**values)

    def random_shell(self) -> Shell:
        lives_unk = self.lives - self.state.count(Shell.live)
        blanks_unk = self.blanks - self.state.count(Shell.blank)
        return random.choices(
            [Shell.live, Shell.blank], weights=[lives_unk, blanks_unk]
        )[0]

    @check_item(item=Item.handcuff)
    def ac_handcuff(self) -> bool:
        if self.player_turn and not self.dealer_handcuff:
            self.dealer_handcuff = True
            return True
        if not self.player_turn and not self.player_handcuff:
            self.player_handcuff = True
            return True
        return False

    @check_item(item=Item.magnifier)
    def ac_magnifier(self) -> bool:
        if self.state[-1] == Shell.unknown:
            self.state[-1] = self.random_shell()
        return True

    @check_item(item=Item.saw)
    def ac_saw(self) -> bool:
        if self.saw_bonus == 1:
            self.saw_bonus = 2
            return True
        return False

    @check_item(item=Item.phone)
    def ac_phone(self) -> bool:
        if len(self.state) > 1:
            id_shell = random.randint(0, len(self.state) - 1)
            if self.state[id_shell] == Shell.unknown:
                self.state[id_shell] = self.random_shell()
            return True
        return False

    @check_item(item=Item.beer)
    def ac_beer(self) -> bool:
        if self.state[-1] == Shell.unknown:
            self.state[-1] = self.random_shell()

        if self.state[-1] == Shell.live:
            self.lives -= 1
        elif self.state[-1] == Shell.blank:
            self.blanks -= 1
        del self.state[-1]
        return True

    @check_item(item=Item.cigarette)
    def ac_cigarette(self) -> bool:
        if self.player_turn and self.player_life < self.max_life:
            self.player_life += 1
            return True
        if not self.player_turn and self.dealer_life < self.max_life:
            self.dealer_life += 1
            return True
        return False

    @check_item(item=Item.medecine)
    def ac_medecine(self) -> bool:
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
        return True

    def check_adrenaline(self) -> bool:
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

    @check_item(item=Item.adrenaline)
    def ac_adrenaline(self) -> bool:
        if self.check_adrenaline():
            if self.player_turn:
                item = random.choice(
                    [i for i in self.items_dealer if i != Item.adrenaline]
                )
                self.action(item)
                self.items_dealer.remove(item)
            else:
                item = random.choice(
                    [i for i in self.items_player if i != Item.adrenaline]
                )
                self.action(item)
                self.items_player.remove(item)
            return True
        return False

    def ac_shoot_opposite(self) -> bool:
        if self.state[-1] == Shell.unknown:
            self.state[-1] = self.random_shell()

        if self.state[-1] == Shell.live:
            if self.player_turn:
                self.dealer_life -= 1
            else:
                self.player_life -= 1
            self.lives -= 1
        else:
            self.blanks -= 1
        self.change_turn()
        del self.state[-1]
        return True

    def ac_shoot_self(self) -> bool:
        if self.state[-1] == Shell.unknown:
            self.state[-1] = self.random_shell()

        if self.state[-1] == Shell.live:
            if self.player_turn:
                self.player_life -= 1
            else:
                self.dealer_life -= 1
            self.lives -= 1
            self.change_turn()
        else:
            self.blanks -= 1
        del self.state[-1]
        return True

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

    def action(self, action: int) -> bool:
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
                return self.ac_shoot_self()
        return False
