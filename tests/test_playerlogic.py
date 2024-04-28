from pytest import fixture

from buckshot_solver.elements import Action, Shell
from buckshot_solver.playerlogic import PlayerLogic
from buckshot_solver.round import Round


@fixture
def logic() -> PlayerLogic:
    return PlayerLogic()


@fixture
def one_live() -> Round:
    return Round(
        lives=1,
        blanks=0,
        max_life=5,
        player_life=4,
        dealer_life=5,
        items_player=[],
        items_dealer=[],
        player_turn=True,
        shells=[Shell.unknown],
    )


@fixture
def one_blank() -> Round:
    return Round(
        lives=0,
        blanks=1,
        max_life=5,
        player_life=4,
        dealer_life=5,
        items_player=[],
        items_dealer=[],
        player_turn=True,
        shells=[Shell.unknown],
    )


def test_choose_actions_one_live(logic: PlayerLogic, one_live: Round) -> None:
    assert logic.choose_actions(one_live) == [Action.opponent.value]


def test_choose_actions_one_blank(logic: PlayerLogic, one_blank: Round) -> None:
    assert logic.choose_actions(one_blank) == [Action.myself.value]
