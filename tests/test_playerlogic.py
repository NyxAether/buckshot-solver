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
    )

@fixture
def three_bullet() -> Round:
    return Round(
        lives=1,
        blanks=2,
        max_life=5,
        player_life=4,
        dealer_life=5,
        items_player=[],
        items_dealer=[],
        player_turn=True,
    )


def test_choose_actions_one_live(logic: PlayerLogic, one_live: Round) -> None:
    _, actions = logic.choose_actions(one_live)
    assert actions == [Action.opponent.value]


def test_choose_actions_one_blank(logic: PlayerLogic, one_blank: Round) -> None:
    _, actions = logic.choose_actions(one_blank)
    assert actions == [Action.myself.value]

def test_choose_actions_three_bullet(logic: PlayerLogic, three_bullet: Round) -> None:
    three_bullet.shells[-3] = Shell.live
    three_bullet.player_shells[-3] = Shell.live
    p, actions = logic.choose_actions(three_bullet)
    assert actions == [Action.myself]
    assert p == 1.0