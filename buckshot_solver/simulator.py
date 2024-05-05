from collections import defaultdict
from itertools import combinations
from typing import Generator

from buckshot_solver.elements import Action, Shell
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

    def start(self) -> defaultdict[Action, float]:
        for shells in self._generate_all_outcomes():
            cr = self.frozen_round.copy_round()
            cr.shells = shells
        return defaultdict(float)
