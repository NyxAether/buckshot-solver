from collections import defaultdict
from multiprocessing.pool import Pool
from typing import Generator

from buckshot_solver.dealerlogic import DealerLogic
from buckshot_solver.round import Round
from buckshot_solver.simulation import Simulation


class Simulator:
    def __init__(
        self,
        base_round: Round,
        nb_simulations: int = 10_000,
    ):
        self.frozen_round = base_round
        self.nb_simulations = nb_simulations

    def _score_round(self, cr: Round) -> float:
        if cr.player_life == 0:
            return -20
        if cr.dealer_life == 0:
            return 20
        return (
            cr.player_life * 0.75
            + (cr.max_life - cr.dealer_life)
            + 0.1 * len(cr.items_player)
        )

    def _simulate_round(self, action: int, cr: Round) -> tuple[int, int, float]:
        proba = Simulation(cr).start(action)
        return action, proba, self._score_round(cr)

    def _generator_simulations(self) -> Generator[tuple[int, Round], None, None]:
        for _ in range(self.nb_simulations):
            for action in self.frozen_round.possible_actions:
                cr = Round.from_round(self.frozen_round)
                yield (action, cr)

    def start(self) -> defaultdict[int, float]:
        frozen_score = self._score_round(self.frozen_round)
        scores: defaultdict[int, float] = defaultdict(float)
        # probas: defaultdict[int, int] = defaultdict(int)
        pool = Pool()
        res = pool.starmap_async(self._simulate_round, self._generator_simulations())
        pool.close()
        pool.join()
        for action, proba, score in res.get():
            scores[action] += score - frozen_score
        # for action in scores:
        #     scores[action] /= probas[action]
        return scores

    def dealer_act(self) -> None:
        dealer = DealerLogic()
        _, actions = dealer.choose_actions(self.frozen_round)
        for action in actions:
            self.frozen_round.action(action)
