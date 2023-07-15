from model.fpl_team import BaseFPL

class FPLGoalkeeper(BaseFPL):
    def __init__(self, budget):
        super().__init__()
        self.number_of_goalkeepers_count = 2
        self.budget = budget
        
    def min_no_of_players(self):
        return 2
        
    def validate_player(self, full_name, cost, team):
        in_budget = self.validate_budget(cost, full_name, self.budget)
        team_limit = self.validate_team_tracker(team)
        
        if in_budget and team_limit:
            return True
        else:
            return False
        
    def decrement_star_players(self, cost):
        pass
