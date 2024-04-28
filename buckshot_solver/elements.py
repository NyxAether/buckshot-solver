from enum import IntEnum


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
