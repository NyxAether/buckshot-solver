from enum import IntEnum
from functools import total_ordering
from typing import Iterable

from pydantic import BaseModel


class ShotType(IntEnum):
    opponent: int = 8
    self: int = 9


class Shell(IntEnum):
    unknown: int = -1
    blank: int = 0
    live: int = 1


class Item(IntEnum):
    handcuff: int = 0
    magnifier: int = 1
    saw: int = 2
    phone: int = 3
    beer: int = 4
    cigarette: int = 5
    medecine: int = 6
    adrenaline: int = 7
    inverter: int = 8

    @classmethod
    def from_str(cls, name: str) -> "Item":
        return getattr(cls, name)


class Action(IntEnum):
    handcuff: int = 0
    magnifier: int = 1
    saw: int = 2
    phone: int = 3
    beer: int = 4
    cigarette: int = 5
    medecine: int = 6
    adrenaline: int = 7
    inverter: int = 8
    opponent: int = 9
    myself: int = 10

    @classmethod
    def int_to_str(cls, value: int) -> str:
        return Action(value).name

    @classmethod
    def from_item(cls, item: Item) -> "Action":
        return Action(item.value)

    def __str__(self) -> str:
        return f"{self.name}"


@total_ordering
class RouletteResult(BaseModel):
    player_life: int | float = 0
    dealer_life: int | float = 0

    @property
    def score(self) -> float:
        return self.player_life * 0.75 + self.dealer_life * -1.0

    def __add__(self, other: "RouletteResult") -> "RouletteResult":
        if not isinstance(other, RouletteResult):
            raise NotImplementedError
        return RouletteResult(
            player_life=self.player_life + other.player_life,
            dealer_life=self.dealer_life + other.dealer_life,
        )

    def __truediv__(self, other: int | float) -> "RouletteResult":
        if not isinstance(other, int) and not isinstance(other, float):
            raise NotImplementedError
        return RouletteResult(
            player_life=self.player_life / other,
            dealer_life=self.dealer_life / other,
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RouletteResult):
            raise NotImplementedError
        return (
            self.player_life == value.player_life
            and self.dealer_life == value.dealer_life
        ) or self.score == value.score

    def __lt__(self, value: object) -> bool:
        if not isinstance(value, RouletteResult):
            raise NotImplementedError
        return self.score < value.score


def sum_res(results: Iterable[RouletteResult]) -> RouletteResult:
    res = RouletteResult(player_life=0, dealer_life=0)
    for r in results:
        res += r
    return res
