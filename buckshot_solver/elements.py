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


class Action(IntEnum):
    handcuff: int = 0
    magnifier: int = 1
    saw: int = 2
    phone: int = 3
    beer: int = 4
    cigarette: int = 5
    medecine: int = 6
    adrenaline: int = 7
    opponent: int = 8
    myself: int = 9
