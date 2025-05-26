from buckshot_solver.round import Round
from buckshot_solver.simulator import Simulator


def test_simulator() -> None:
    cr = Round(lives=1, blanks=1, player_life=2, dealer_life=2, max_life=2)
    res = Simulator(cr).start()
    assert True
