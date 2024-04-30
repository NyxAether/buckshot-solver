import random
from functools import wraps
from typing import Any, Callable, Self

from pydantic import BaseModel, field_serializer, model_validator

from buckshot_solver.elements import Action, Item, Shell

class RoundError(Exception):
    pass

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
            raise RoundError(f"Item {item.name} not available")

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
    inverted: bool = False
    saw_bonus: int = 1
    items_player: list[Item] = []
    items_dealer: list[Item] = []
    shells: list[Shell] = []
    player_shells: list[Shell] = []
    dealer_shells: list[Shell] = []

    #  Serializers
    @field_serializer("items_player")
    def serialize_items_player(self, items_player: list[Item]) -> list[str]:
        return [i.name for i in self.items_player]

    @field_serializer("items_dealer")
    def serialize_items_dealer(self, items_dealer: list[Item]) -> list[str]:
        return [i.name for i in self.items_dealer]

    @field_serializer("player_shells")
    def serialize_player_shells(self, player_shells: list[Shell]) -> list[str]:
        map_dict = {Shell.unknown: "U", Shell.live: "L", Shell.blank: "B"}
        return [map_dict[s] for s in self.player_shells]

    # End of serializers

    # Validators

    @model_validator(mode="after")
    def check_health_valid(self) -> Self:
        if self.player_life < 0 or self.dealer_life < 0:
            raise ValueError("Health can't be negative")
        if self.player_life > self.max_life or self.dealer_life > self.max_life:
            raise ValueError("Health can't be greater than max_life")
        return self

    @model_validator(mode="after")
    def check_shells_valid(self) -> Self:
        if len(self.shells) != self.lives + self.blanks:
            raise ValueError("Wrong number of shells")
        return self

    # End of validators

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

    def _remove_last_shell(self) -> Shell:
        last_shell = self.shells[-1]
        if self.inverted:
            if last_shell == Shell.live:
                last_shell = Shell.blank
                self.lives -= 1
                self.blanks += 1
            elif last_shell == Shell.blank:
                last_shell = Shell.live
                self.lives += 1
                self.blanks -= 1
            else:
                ValueError("Trying to remove an unknown shell")
        del self.shells[-1]
        del self.player_shells[-1]
        del self.dealer_shells[-1]
        self.update_both_knowledge()
        return last_shell

    def _resolve_shells(self, shells: list[Shell], shell: Shell) -> None:
        for i, s in enumerate(shells):
            if s == Shell.unknown:
                shells[i] = shell

    def _update_knowledge(self, shells: list[Shell]) -> None:
        # Player
        remain_lives = self.lives - shells.count(Shell.live)
        remain_blanks = self.blanks - shells.count(Shell.blank)
        if remain_lives == 0:
            self._resolve_shells(shells, Shell.blank)
        if remain_blanks == 0:
            self._resolve_shells(shells, Shell.live)

    def update_both_knowledge(self) -> None:
        self._update_knowledge(self.player_shells)
        self._update_knowledge(self.dealer_shells)

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
        self.update_both_knowledge()
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
            self.update_both_knowledge()
            self._remove_played_item(Item.phone)
            return proba
        return 0.0

    @check_item(item=Item.beer)
    def ac_beer(self) -> float:
        proba = 1.0
        last_shell = self._remove_last_shell()
        if last_shell == Shell.live:
            self.lives -= 1
        elif last_shell == Shell.blank:
            self.blanks -= 1
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

    @check_item(item=Item.inverter)
    def ac_inverter(self) -> float:
        self.inverted = not self.inverted
        self._remove_played_item(Item.inverter)
        return 1.0

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
        last_shell = self._remove_last_shell()
        if last_shell == Shell.live:
            if self.player_turn:
                self.dealer_life -= 1 * self.saw_bonus
            else:
                self.player_life -= 1 * self.saw_bonus
            self.lives -= 1
        else:
            self.blanks -= 1
        self.saw_bonus = 1
        self.change_turn()
        return 1.0

    def ac_shoot_myself(self) -> float:
        last_shell = self._remove_last_shell()
        if last_shell == Shell.live:
            if self.player_turn:
                self.player_life -= 1 * self.saw_bonus
            else:
                self.dealer_life -= 1 * self.saw_bonus
            self.lives -= 1
            self.change_turn()
        else:
            self.blanks -= 1
        self.saw_bonus = 1
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

    def action(self, action: Action) -> float:
        match action:
            case Action.handcuff:
                return self.ac_handcuff()
            case Action.magnifier:
                return self.ac_magnifier()
            case Action.saw:
                return self.ac_saw()
            case Action.phone:
                return self.ac_phone()
            case Action.beer:
                return self.ac_beer()
            case Action.cigarette:
                return self.ac_cigarette()
            case Action.medecine:
                return self.ac_medecine()
            case Action.inverter:
                return self.ac_inverter()
            case Action.adrenaline:
                return self.ac_adrenaline()
            case Action.opponent:
                return self.ac_shoot_opposite()
            case Action.myself:
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
