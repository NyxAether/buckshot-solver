from pytest import fixture

from buckshot_solver.elements import Item, Shell
from buckshot_solver.round import Round


@fixture
def new_round() -> Round:
    return Round(
        lives=3,
        blanks=2,
        max_life=5,
        player_life=4,
        dealer_life=5,
        items_player=[
            Item.handcuff,
            Item.magnifier,
            Item.saw,
            Item.phone,
            Item.beer,
            Item.cigarette,
            Item.medecine,
        ],
        items_dealer=[
            Item.handcuff,
            Item.saw,
            Item.phone,
            Item.beer,
            Item.cigarette,
            Item.medecine,
        ],
    )

@fixture
def adrenaline_round() -> Round:
    return Round(
        lives=3,
        blanks=2,
        max_life=5,
        player_life=4,
        dealer_life=5,
        items_player=[
            Item.saw,
        ],
        items_dealer=[
            Item.adrenaline,
        ],
    )

@fixture
def adrenaline_round2() -> Round:
    return Round(
        lives=3,
        blanks=2,
        max_life=5,
        player_life=4,
        dealer_life=5,
        items_player=[
            Item.adrenaline,
        ],
        items_dealer=[
            Item.saw,
        ],
    )


def test_from_round(new_round: Round) -> None:
    c_round = Round.from_round(new_round)
    assert c_round.lives == 3
    assert c_round.blanks == 2
    assert c_round.max_life == 5
    assert c_round.player_life == 4
    assert c_round.dealer_life == 5
    assert c_round.items_player == [
        Item.handcuff,
        Item.magnifier,
        Item.saw,
        Item.phone,
        Item.beer,
        Item.cigarette,
        Item.medecine,
    ]
    assert c_round.items_dealer == [
        Item.handcuff,
        Item.saw,
        Item.phone,
        Item.beer,
        Item.cigarette,
        Item.medecine,
    ]
    assert c_round.shells == [Shell.unknown] * (3 + 2)
    assert c_round.player_turn
    assert not c_round.player_handcuff
    assert not c_round.dealer_handcuff
    assert c_round.saw_bonus == 1


def test_ac_handcuff(new_round: Round) -> None:
    new_round.ac_handcuff()
    assert not new_round.player_handcuff
    assert new_round.dealer_handcuff
    assert Item.handcuff not in new_round.items_player


def test_ac_handcuff_2(new_round: Round) -> None:
    new_round.player_turn = False
    new_round.ac_handcuff()
    assert new_round.player_handcuff
    assert not new_round.dealer_handcuff
    assert Item.handcuff not in new_round.items_dealer


def test_ac_magnifier(new_round: Round) -> None:
    new_round.ac_magnifier()
    assert new_round.shells[-1] != Shell.unknown
    assert Item.magnifier not in new_round.items_player


def test_ac_saw(new_round: Round) -> None:
    new_round.ac_saw()
    assert new_round.saw_bonus == 2
    assert not new_round.ac_saw()
    assert Item.saw not in new_round.items_player


def test_ac_phone(new_round: Round) -> None:
    new_round.ac_phone()
    assert new_round.shells.count(Shell.unknown) == 4
    assert Item.phone not in new_round.items_player


def test_ac_beer(new_round: Round) -> None:
    new_round.ac_beer()
    assert new_round.shells.count(Shell.unknown) == 4
    assert new_round.lives + new_round.blanks == 4
    assert Item.beer not in new_round.items_player


def test_ac_cigarette(new_round: Round) -> None:
    new_round.ac_cigarette()
    assert new_round.player_life == 5
    assert Item.cigarette not in new_round.items_player


def test_ac_cigarette_2(new_round: Round) -> None:
    new_round.player_turn = False
    new_round.ac_cigarette()
    assert new_round.dealer_life == 5
    assert Item.cigarette not in new_round.items_dealer


def test_ac_medecine(new_round: Round) -> None:
    new_round.ac_medecine()
    assert new_round.player_life == 5 or new_round.player_life == 3
    assert Item.medecine not in new_round.items_player


def test_ac_medecine_2(new_round: Round) -> None:
    new_round.player_turn = False
    new_round.ac_medecine()
    assert new_round.dealer_life == 5 or new_round.dealer_life == 4
    assert Item.medecine not in new_round.items_dealer

def test_ac_adrenaline(adrenaline_round: Round) -> None:
    adrenaline_round.player_turn = False
    adrenaline_round.ac_adrenaline()
    assert Item.saw not in adrenaline_round.items_player
    assert Item.adrenaline not in adrenaline_round.items_dealer
    assert Item.saw in adrenaline_round.items_dealer

def test_ac_adrenaline2(adrenaline_round2: Round) -> None:
    adrenaline_round2.ac_adrenaline()
    assert Item.saw not in adrenaline_round2.items_dealer
    assert Item.adrenaline not in adrenaline_round2.items_player
    assert Item.saw in adrenaline_round2.items_player


def test_ac_shoot_self(new_round: Round) -> None:
    new_round.shells[-1] = Shell.live
    new_round.ac_shoot_myself()
    assert new_round.shells[-1] == Shell.unknown
    assert new_round.lives == 2
    assert new_round.blanks == 2
    assert new_round.player_life == 3
    assert not new_round.player_turn


def test_ac_shoot_self_2(new_round: Round) -> None:
    new_round.shells[-1] = Shell.live
    new_round.ac_handcuff()
    new_round.ac_shoot_myself()
    assert new_round.shells[-1] == Shell.unknown
    assert new_round.lives == 2
    assert new_round.blanks == 2
    assert new_round.player_life == 3
    assert new_round.player_turn


def test_ac_shoot_self_3(new_round: Round) -> None:
    new_round.shells[-1] = Shell.blank
    new_round.ac_shoot_myself()
    assert new_round.shells[-1] == Shell.unknown
    assert new_round.lives == 3
    assert new_round.blanks == 1
    assert new_round.player_life == 4
    assert new_round.player_turn


def test_ac_shoot_self_4(new_round: Round) -> None:
    new_round.shells[-1] = Shell.blank
    new_round.ac_handcuff()
    new_round.ac_shoot_myself()
    assert new_round.shells[-1] == Shell.unknown
    assert new_round.lives == 3
    assert new_round.blanks == 1
    assert new_round.player_life == 4
    assert new_round.player_turn
    assert new_round.dealer_handcuff


def test_ac_shoot_opposite(new_round: Round) -> None:
    new_round.shells[-1] = Shell.live
    new_round.ac_shoot_opposite()
    assert new_round.shells[-1] == Shell.unknown
    assert new_round.lives == 2
    assert new_round.blanks == 2
    assert new_round.player_life == 4
    assert new_round.dealer_life == 4
    assert not new_round.player_turn


def test_ac_shoot_opposite_2(new_round: Round) -> None:
    new_round.shells[-1] = Shell.live
    new_round.player_turn = False
    new_round.ac_shoot_opposite()
    assert new_round.shells[-1] == Shell.unknown
    assert new_round.lives == 2
    assert new_round.blanks == 2
    assert new_round.player_life == 3
    assert new_round.dealer_life == 5
    assert new_round.player_turn


def test_ac_shoot_opposite_saw(new_round: Round) -> None:
    new_round.shells[-1] = Shell.live
    new_round.saw_bonus = 2
    new_round.ac_shoot_opposite()
    assert new_round.shells[-1] == Shell.unknown
    assert new_round.lives == 2
    assert new_round.blanks == 2
    assert new_round.player_life == 4
    assert new_round.dealer_life == 3
    assert not new_round.player_turn
    assert new_round.saw_bonus == 1


def test_ac_shoot_myself_saw(new_round: Round) -> None:
    new_round.shells[-1] = Shell.live
    new_round.saw_bonus = 2
    new_round.ac_shoot_myself()
    assert new_round.shells[-1] == Shell.unknown
    assert new_round.lives == 2
    assert new_round.blanks == 2
    assert new_round.player_life == 2
    assert new_round.dealer_life == 5
    assert not new_round.player_turn
    assert new_round.saw_bonus == 1
