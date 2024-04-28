from pytest import fixture

from buckshot_solver.elements import Action, Item, Shell
from buckshot_solver.simulator import Simulator


@fixture
def sim1() -> Simulator:
    return Simulator(
        lives=1,
        blanks=2,
        max_life=5,
        items_player=[],
        items_dealer=[],
    )


@fixture
def sim2() -> Simulator:
    return Simulator(
        lives=2,
        blanks=2,
        max_life=5,
        items_player=[],
        items_dealer=[],
    )


@fixture
def sim3() -> Simulator:
    return Simulator(
        lives=1,
        blanks=1,
        max_life=5,
        items_player=[],
        items_dealer=[],
    )


@fixture
def sim4() -> Simulator:
    return Simulator(
        lives=1,
        blanks=2,
        max_life=2,
        items_player=[],
        items_dealer=[],
    )

@fixture
def sim5() -> Simulator:
    return Simulator(
        lives=2,
        blanks=2,
        max_life=2,
        items_player=[Item.saw],
        items_dealer=[],
    )


def test_simulator_standard1(sim1: Simulator) -> None:
    res = sim1.start()
    assert res[Action.opponent] > res[Action.myself]


def test_simulator_standard2(sim2: Simulator) -> None:
    res = sim2.start()
    assert res[Action.opponent] > res[Action.myself]


def test_simulator_standard3(sim3: Simulator) -> None:
    res = sim3.start()
    assert abs(res[Action.opponent] - res[Action.myself]) < 1


def test_simulator_magnifier(sim3: Simulator) -> None:
    sim3.frozen_round.items_player.append(Item.magnifier)
    res = sim3.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.magnifier


def test_simulator_handcuff(sim3: Simulator) -> None:
    sim3.frozen_round.items_player.append(Item.handcuff)
    res = sim3.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.handcuff


def test_simulator_phone(sim3: Simulator) -> None:
    sim3.frozen_round.items_player.append(Item.phone)
    res = sim3.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.phone


def test_simulator_beer(sim3: Simulator) -> None:
    sim3.frozen_round.items_player.append(Item.beer)
    res = sim3.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.beer


def test_simulator_adrenaline(sim3: Simulator) -> None:
    sim3.frozen_round.items_player.append(Item.adrenaline)
    sim3.frozen_round.items_dealer.append(Item.magnifier)
    res = sim3.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.adrenaline


def test_simulator_saw(sim3: Simulator) -> None:
    sim3.frozen_round.items_player.append(Item.saw)
    sim3.frozen_round.shells[-1] = Shell.live
    sim3.frozen_round.player_shells[-1] = Shell.live
    res = sim3.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.saw


def test_simulator_shoot_self(sim4: Simulator) -> None:
    sim4.frozen_round.shells[-2] = Shell.live
    sim4.frozen_round.player_shells[-2] = Shell.live
    res = sim4.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.myself


def test_simulator_2_beers(sim4: Simulator) -> None:
    sim4.frozen_round.shells[-3] = Shell.live
    sim4.frozen_round.player_shells[-3] = Shell.live
    sim4.frozen_round.dealer_life = 1
    res = sim4.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.myself

def test_simulator_weird_shoot_self(sim5: Simulator) -> None:
    sim5.frozen_round.shells[-4] = Shell.live
    sim5.frozen_round.player_shells[-4] = Shell.live
    sim5.frozen_round.dealer_handcuff = True
    res = sim5.start()
    action_max = max(res, key=res.__getitem__)
    assert action_max == Action.myself
