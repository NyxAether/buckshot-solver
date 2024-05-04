import time
from multiprocessing import Process

from pytest import fixture

from buckshot_solver.elements import Item
from buckshot_solver.round import Round
from buckshot_solver.simulation import Simulation


@fixture
def cr() -> Round:
    return Round(
        lives=1,
        blanks=2,
        max_life=5,
        player_life=5,
        dealer_life=5,
    )


@fixture
def complex_round() -> Round:
    return Round(
        lives=3,
        blanks=3,
        max_life=2,
        player_life=2,
        dealer_life=2,
        items_player=[
            Item.cigarette,
            Item.magnifier,
            Item.medecine,
            Item.inverter,
            Item.saw,
            Item.saw,
        ],
        items_dealer=[
            Item.cigarette,
            Item.beer,
            Item.phone,
            Item.magnifier,
            Item.adrenaline,
            Item.beer,
            Item.handcuff,
        ],
    )


@fixture
def complex_round_2() -> Round:
    return Round(
        lives=4,
        blanks=4,
        max_life=4,
        player_life=4,
        dealer_life=2,
        items_player=[Item.cigarette, Item.inverter, Item.saw, Item.adrenaline],
        items_dealer=[Item.inverter, Item.inverter, Item.medecine, Item.handcuff],
    )


def test_simulation_stop(cr: Round) -> None:
    sim = Simulation(cr)
    proc = Process(target=sim.start)
    proc.start()
    time.sleep(1)
    if proc.is_alive():
        proc.terminate()
        assert False
    proc.join()
    assert True


def test_simulation_complex_run(complex_round: Round) -> None:
    sim = Simulation(complex_round)
    sim.start()
    assert True


def test_simulation_complex_run_2(complex_round_2: Round) -> None:
    sim = Simulation(complex_round_2)
    sim.start()
    assert True
