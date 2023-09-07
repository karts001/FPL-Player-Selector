from src.model.fpl_squad import BaseFPL

class FPLAttack(BaseFPL):
    def __init__(self, star_players, budget):
        super().__init__()
        self.star_players = star_players
        self.star_player_price = 8.0
        self.player_count = self.get_player_count()
        self.budget = budget
        
    def min_no_of_players(self):
        return 3

    def validate_player(self, full_name, cost, team):
        if self.star_players == 0 and cost >= 8.0:
            return False
    
        in_budget = self.validate_budget(cost, full_name, self.budget)
        team_limit = self.validate_team_tracker(team)
        
        if in_budget and team_limit:
            return True
        else:
            return False
        
    def decrement_star_players(self, cost):
        if cost >= 8.0:
            self.star_players -= 1
        
    
    