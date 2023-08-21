"""FPL team class"""

# In starting 11 there must be:
# 1 Goal keeper
# Min 3 defenders
# Min 1 striker
# 11 players total

class FPLTeam:
    def __init__(self):
        self.team_score = 0
        self.team = []
        self.bench = []
        self.goalkeeper = 0
        self.defenders = 0
        self.midfielders = 0
        self.attackers = 0
        self.validation_tracker = {}
        
    def validate_team(self):
        if self.validate_goalkeeper() and self.validate_defenders() and self.validate_attackers():
            return True
        else:
            self.validation_tracker.update({
                "goalkeeper": self.validate_goalkeeper(),
                "defenders": self.validate_defenders(),
                "attackers": self.validate_attackers()
            })
            
            return False
            
    
    def validate_goalkeeper(self):
        if self.goalkeeper != 1:
            return False
        else:
            return True
        
    def validate_defenders(self):
        if self.defenders < 3:
            return False
        else:
            return True
        
    def validate_attackers(self):
        if self.attackers < 1:
            return False
        else:
            return True
    
    def increment_position_counter(self, element):
        if element == 1:
            self.goalkeeper += 1
        if element == 2:
            self.defenders += 1
        if element == 3:
            self.midfielders += 1
        if element == 4:
            self.attackers += 1