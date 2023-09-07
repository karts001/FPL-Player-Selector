from src.model.fpl_squad import BaseFPL

class FPLDefender(BaseFPL):
    def __init__(self, star_players, budget):
        super().__init__()
        self.star_players = star_players
        self.number_of_defenders_count = 5
        self.star_player_price = 6.0
        self.budget = budget
        
    def min_no_of_players(self):
        return 5
          
    def validate_player(self, full_name, cost, team):
        if self.star_players == 0 and cost >= 6.0:
            return False
        
        if len(self.players) == 3 and cost >= 5.0:
            return False
    
        in_budget = self.validate_budget(cost, full_name, self.budget)
        team_limit = self.validate_team_tracker(team)
        
        if in_budget and team_limit:
            return True
        else:
            return False
        
    def decrement_star_players(self, cost):
        if cost >= 6.0:
            self.star_players -= 1   
