from enum import IntEnum


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
