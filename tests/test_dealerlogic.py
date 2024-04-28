from pytest import fixture

from buckshot_solver.dealerlogic import DealerLogic
from buckshot_solver.elements import Action, Item, Shell
from buckshot_solver.round import Round


@fixture
def cr() -> Round:
    return Round(
        lives=3,
        blanks=2,
        max_life=5,
        player_life=4,
        dealer_life=5,
        items_player=[],
        items_dealer=[],
        player_turn=False,
    )


@fixture
def cr2() -> Round:
    return Round(
        lives=1,
        blanks=1,
        max_life=5,
        player_life=4,
        dealer_life=5,
        items_player=[],
        items_dealer=[],
        player_turn=False,
    )


def test_choose_action(cr: Round) -> None:
    dealer = DealerLogic()
    cr.items_player.append(Item.saw)
    cr.items_dealer.append(Item.adrenaline)
    cr.shells[-1] = Shell.live
    cr.dealer_shells[-1] = Shell.live
    _, actions = dealer.choose_actions(cr)
    assert Action.adrenaline in actions


def test_choose_action2(cr: Round) -> None:
    dealer = DealerLogic()
    cr.items_player.append(Item.saw)
    cr.items_dealer.append(Item.adrenaline)
    cr.shells[-1] = Shell.blank
    cr.dealer_shells[-1] = Shell.blank
    actions = dealer.choose_actions(cr)
    assert Action.opponent not in actions


def test_choose_action3(cr: Round) -> None:
    dealer = DealerLogic()
    _, actions = dealer.choose_actions(cr)
    assert Action.opponent in actions


def test_choose_action4(cr2: Round) -> None:
    dealer = DealerLogic()
    proba, actions = dealer.choose_actions(cr2)
    assert proba == 0.5
