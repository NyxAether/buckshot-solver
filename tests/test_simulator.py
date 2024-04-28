from pytest import fixture

from buckshot_solver.elements import Action, Item
from buckshot_solver.simulator import Simulator


@fixture
def simulator1() -> Simulator:
    return Simulator(
        lives=1,
        blanks=2,
        max_life=5,
        items_player=[],
        items_dealer=[],
    )


@fixture
def simulator2() -> Simulator:
    return Simulator(
        lives=2,
        blanks=2,
        max_life=5,
        items_player=[],
        items_dealer=[],
    )


@fixture
def simulator3() -> Simulator:
    return Simulator(
        lives=1,
        blanks=1,
        max_life=5,
        items_player=[],
        items_dealer=[],
    )


@fixture
def simulator4() -> Simulator:
    return Simulator(
        lives=2,
        blanks=3,
        max_life=5,
        items_player=[Item.handcuff, Item.saw],
        items_dealer=[Item.adrenaline],
    )


def test_simulator_standard1(simulator1: Simulator) -> None:
    res = simulator1.start()
    assert res[Action.opponent] > res[Action.myself]


def test_simulator_standard2(simulator2: Simulator) -> None:
    res = simulator2.start()
    assert res[Action.opponent] > res[Action.myself]


def test_simulator_standard3(simulator3: Simulator) -> None:
    res = simulator3.start()
    assert (
        abs(res[Action.opponent] - res[Action.myself]) < simulator3.nb_simulations // 10
    )


def test_simulator_magnifier(simulator3: Simulator) -> None:
    simulator3.frozen_round.items_player.append(Item.magnifier)
    res = simulator3.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.magnifier


def test_simulator_handcuff(simulator3: Simulator) -> None:
    simulator3.frozen_round.items_player.append(Item.handcuff)
    res = simulator3.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.handcuff


def test_simulator_phone(simulator3: Simulator) -> None:
    simulator3.frozen_round.items_player.append(Item.phone)
    res = simulator3.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.phone


def test_simulator_beer(simulator3: Simulator) -> None:
    simulator3.frozen_round.items_player.append(Item.beer)
    res = simulator3.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.beer


def test_simulator_adrenaline(simulator3: Simulator) -> None:
    simulator3.frozen_round.items_player.append(Item.adrenaline)
    simulator3.frozen_round.items_dealer.append(Item.magnifier)
    res = simulator3.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.adrenaline


def test_simulator_saw(simulator3: Simulator) -> None:
    simulator3.frozen_round.items_player.append(Item.saw)
    res = simulator3.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.myself

