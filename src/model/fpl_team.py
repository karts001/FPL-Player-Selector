""" Create an FPL class which contains all the rules of the FPL team """

NUMBER_OF_PLAYERS_IN_SQUAD = 15

class FPLTeam():
    def __init__(self, star_players):
        self.player_count = 0
        self.number_of_goal_keeper_in_squad = 2
        self.number_of_defenders_in_squad = 5
        self.number_of_midfielders_in_squad = 5
        self.number_of_attackers_in_squad = 3
        self.goalkeeper_count = 0
        self.defender_count = 0
        self.midfield_count = 0
        self.attack_count = 0
        self.budget = 100
        self.team = []
        self.star_players = star_players
        self.team_tracker = {}
        self.average_player_cost = self.calculate_new_average_player_cost()
                    
    def validate_player(self, full_name, cost, team, position):
        
        if self.star_players == 0 and cost > 8.0:
            return False
        
        in_budget = self.validate_budget(cost, full_name)
        position_limit = self.validate_squad_position(position)
        team_limit = self.validate_team_tracker(team)

        if in_budget and position_limit and team_limit:
            return True
        else:
            return False
    
    def add_player(self, cost, position, full_name, player_team):
        
        self.team.append(full_name)
        self.budget -= cost
        self.increment_player_position_count(position)
        self.increment_team_tracker(player_team)
        self.decrement_star_players(cost)
        self.get_player_count()
        self.calculate_new_average_player_cost()
    
    def calculate_new_average_player_cost(self):
        
        return self.budget / (NUMBER_OF_PLAYERS_IN_SQUAD - self.player_count)
    
    def validate_budget(self, player_cost, player_name):
        if (self.budget - player_cost) < 0:
            # remove previous player
            print(f"Invalid funds for this {player_name}. He costs {player_cost}, the remaining budget is {self.budget}")
            return False
        else:
            return True

    def validate_squad_position(self, position):

        if position == 1 and self.goalkeeper_count == self.number_of_goal_keeper_in_squad:
            print("Already 2 goal keepers in the squad")
            return False
            
        elif position == 2 and self.defender_count == self.number_of_defenders_in_squad:
            print("Already 5 defenders in the squad")
            return False
            
        
        elif position == 3 and self.midfield_count == self.number_of_midfielders_in_squad:
            print("Already 5 midfielders in the squad")
            return False
            
        elif position == 4 and self.attack_count == self.number_of_attackers_in_squad:
            print("Already 3 attackers in the squad")
            return False
        
        else:
            return True

    def validate_team_tracker(self, team):
        
        is_team_in_tracker = self.team_tracker.get(team, None)
        if is_team_in_tracker == None:
            return True
        elif is_team_in_tracker == 3:
            return False
        else:
            return True
        
    def decrement_star_players(self, cost):
        if cost > 8.0:
            self.star_players -= 1
        
    def increment_player_position_count(self, position):
        if position == 1:
            self.goalkeeper_count += 1
        elif position == 2:
            self.defender_count += 1
        elif position == 3:
            self.midfield_count += 1
        elif position == 4:
            self.attack_count += 1    
            
    def get_player_count(self):
        self.player_count = len(self.team)
        
    def increment_team_tracker(self, team_id):
        team = self.team_tracker.get(team_id, None)
        
        if team == None:
            # add new team to dictionary
            self.team_tracker[team_id] = 1
        else:
            self.team_tracker[team_id] += 1
           
       