"""FPL team class"""

from operator import attrgetter

class FPLTeam:
    def __init__(self):
        self.team_score = 0
        self.team = []
        self.bench = []
        
    def select_best_team(self):
        for bench_player in self.bench:
            for starting_player in self.team:
                if starting_player.element_type == 1 and bench_player.element_type != 1:
                    continue
                else:
                    if bench_player.score > starting_player.score:
                        continue
                if bench_player.score < starting_player.score:
                    break
                if bench_player.score > starting_player.score:
                    print("something")
                    