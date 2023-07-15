""" Create an FPL class which contains all the rules of the FPL team """

from abc import ABC, abstractmethod

NUMBER_OF_PLAYERS_IN_SQUAD = 15
NUMBER_OF_GOAL_KEEPERS_IN_SQUAD = 2
NUMBER_OF_GSDEFENDER_IN_SQUAD = 5
NUMBER_OF_MIDFIELDERS_IN_SQUAD = 5
NUMBER_OF_ATTACKERS_IN_SQUAD = 5

team_tracker = {}

class BaseFPL(ABC):
    def __init__(self):
        self.players = []
        self.player_count = 0
    
    @property
    @abstractmethod
    def min_no_of_players(self):
        pass
        
    @abstractmethod
    def validate_player(self, full_name, cost, team):
        pass
    
    @abstractmethod
    def decrement_star_players(self, cost):
        pass
    
    def add_player(self, full_name, cost, team):
        self.players.append(full_name)
        self.budget -= cost
        self.decrement_star_players(cost)
        self.increment_team_tracker(team)
        self.player_count = self.get_player_count()
    
    def validate_budget(self, player_cost, player_name, budget):
        if (self.budget - player_cost) < 0:
            print(f"Invalid funds for this {player_name}. He costs {player_cost}, the remaining budget is {budget}")
            return False
        else:
            return True
    
    def validate_team_tracker(self, team):
        is_team_in_tracker = team_tracker.get(team, None)
        if is_team_in_tracker == None:
            return True
        elif is_team_in_tracker == 3:
            return False
        else:
            return True
    
    def increment_team_tracker(self, team_id):
        team = team_tracker.get(team_id, None)
        
        if team == None:
            # add new team to dictionary
            team_tracker[team_id] = 1
        else:
            team_tracker[team_id] += 1
            
    def get_player_count(self):
        return len(self.players) 
   