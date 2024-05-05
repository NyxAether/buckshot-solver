from buckshot_solver.elements import RouletteResult, sum_res


def test_add() -> None:
    rr = RouletteResult(player_life=1, dealer_life=2)
    assert rr + rr == RouletteResult(player_life=2, dealer_life=4)


def test_sum() -> None:
    rr = RouletteResult(player_life=1, dealer_life=2)
    l: list[RouletteResult] = [rr, rr]
    assert sum_res(l) == RouletteResult(player_life=2, dealer_life=4)


def test_div() -> None:
    rr = RouletteResult(player_life=2, dealer_life=4)
    assert rr / 2 == RouletteResult(player_life=1, dealer_life=2)


def test_lt() -> None:
    rr12 = RouletteResult(player_life=1, dealer_life=2)
    rr22 = RouletteResult(player_life=2, dealer_life=2)
    rr24 = RouletteResult(player_life=2, dealer_life=4)
    assert rr12 < rr22
    assert rr24 < rr12
    assert rr24 < rr22


def test_eq() -> None:
    rr12 = RouletteResult(player_life=1, dealer_life=2)
    rr12 = RouletteResult(player_life=2, dealer_life=4)
    rr152 = RouletteResult(player_life=2, dealer_life=1.5)
    rr34 = RouletteResult(player_life=4, dealer_life=3)
    assert rr12 == rr12
    assert rr152 == rr34
