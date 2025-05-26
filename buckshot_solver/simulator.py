from itertools import combinations
from typing import Generator

from buckshot_solver.elements import Action, RouletteResult, Shell
from buckshot_solver.logics.playerlogic import PlayerLogic
from buckshot_solver.round import Round


class Simulator:
    def __init__(self, base_round: Round):
        self.frozen_round = base_round

    def _generate_all_outcomes(self) -> Generator[list[Shell], None, None]:
        lives = self.frozen_round.lives - self.frozen_round.shells.count(Shell.live)
        unknown_ids = [
            i for i, s in enumerate(self.frozen_round.shells) if s == Shell.unknown
        ]
        shells_no_unk = self.frozen_round.shells.copy()
        for i, shell in enumerate(shells_no_unk):
            if shell == Shell.unknown:
                shells_no_unk[i] = Shell.blank
        for combination in combinations(unknown_ids, lives):
            shells = shells_no_unk.copy()
            for id_shell in combination:
                shells[id_shell] = Shell.live
            yield shells

    def _update_dict(
        self,
        results: dict[Action, RouletteResult],
        new_dict: dict[Action, RouletteResult],
    ) -> None:
        for key, value in new_dict.items():
            results[key] += value

    def start(self) -> dict[Action, RouletteResult]:
        player = PlayerLogic()
        results: dict[Action, RouletteResult] = {}
        for i, shells in enumerate(self._generate_all_outcomes()):
            cr = self.frozen_round.copy_round()
            cr.shells = shells
            self._update_dict(results, player.first_choose_actions(cr))
        i += 1
        for k in results:
            results[k] /= i
        return results
