import time
from multiprocessing import Process

from pytest import fixture

from buckshot_solver.simulation import Simulation
from buckshot_solver.round import Round


@fixture
def cr() -> Round:
    return Round(
        lives=1,
        blanks=2,
        max_life=5,
        player_life=5,
        dealer_life=5,
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
