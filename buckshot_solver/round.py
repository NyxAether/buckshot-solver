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
                if self.adrenaline:
                    if item in self.items_dealer:
                        self.items_dealer.remove(item)
                        self.items_player.append(item)
                        self.adrenaline = False
                    else:
                        RoundError(f"{item} was not in items'dealer")
                if item in self.items_player:
                    return func(self, *args, **kwargs)
            else:
                if self.adrenaline:
                    if item in self.items_player:
                        self.items_player.remove(item)
                        self.items_dealer.append(item)
                        self.adrenaline = False
                    else:
                        RoundError(f"{item} was not in items'player")
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
    adrenaline: bool = False
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

    def copy_round(self) -> "Round":
        return Round.from_round(self)

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

    def remove_played_item(self, item: Item) -> None:
        if self.player_turn:
            self.items_player.remove(item)
        else:
            self.items_dealer.remove(item)

    def remove_last_shell(self) -> Shell:
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
        self.inverted = False
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

    @property
    def possible_actions(self) -> set[Action]:
        possible_shots = {Action.opponent, Action.myself}
        items_self = self.items_player
        items_opp = self.items_dealer
        handcuff_self = self.player_handcuff
        handcuff_opp = self.dealer_handcuff
        if not self.player_turn:
            items_self, items_opp = items_opp, items_self
            handcuff_self, handcuff_opp = handcuff_opp, handcuff_self
        actions_self = {Action.from_item(i) for i in items_self}
        actions_opp = {Action.from_item(i) for i in items_opp}
        actions_opp = actions_opp - {Action.adrenaline}
        if self.saw_bonus == 2:
            actions_self = actions_self - {Action.saw}
            actions_opp = actions_opp - {Action.saw}
        if handcuff_opp:
            actions_self = actions_self - {Action.handcuff}
            actions_opp = actions_opp - {Action.handcuff}
        if len(self.shells) < 2:
            actions_self = actions_self - {Action.phone}
        if len(actions_opp) == 0:
            actions_self = actions_self - {Action.adrenaline}

        if self.adrenaline:
            return actions_opp
        return actions_self.union(possible_shots)

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
