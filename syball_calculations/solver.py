import argparse
import ast
from player_wrapper import Player
from pulp import *

# from integer_program import LPSolver


class Game:
    # fixed
    PLAYERS_PER_TEAM = 9
    NUM_TEAMS = 16
    NUM_CATEGORIES = 9
    MONEY_PER_TEAM = 200
    SPOTS_ALL_TEAMS = PLAYERS_PER_TEAM * NUM_TEAMS # total number of players that need to be drafted
    CATEGORIES = ['threes', 'reb', 'ast', 'stl', 'blk', 'to', 'pts', 'fgm', 'fga', 'ftm', 'fta']
  # gives value to all variables
    def __init__(self):
        self.total_money_remaining = self.NUM_TEAMS * self.MONEY_PER_TEAM 
        self.my_spots_remaining = self.PLAYERS_PER_TEAM
        self.my_money_remaining = self.MONEY_PER_TEAM
        self.player_dict = {}
        for category in self.CATEGORIES:
            setattr(self, '{}_{}'.format("my", category), 0)
            setattr(self, '{}_{}'.format("total", category), 0)
            setattr(self, '{}_{}'.format("avg", category), 0)
        self.avg_fg = 0
        self.avg_ft = 0

    # gives total counts for all stats in player_dict
    def recompute_totals(self):
        for player in self.player_dict.values():
            for category in self.CATEGORIES:
                setattr(self, '{}_{}'.format("total", category), getattr(self, '{}_{}'.format("total", category)) + getattr(player, category.upper()))
    # compute team averages
    def compute_team_averages(self):
        self.avg_threes = self.total_threes / self.NUM_TEAMS
        self.avg_reb = self.total_reb / self.NUM_TEAMS
        self.avg_ast = self.total_ast / self.NUM_TEAMS
        self.avg_stl = self.total_stl / self.NUM_TEAMS
        self.avg_blk = self.total_blk / self.NUM_TEAMS
        self.avg_to = self.total_to / self.NUM_TEAMS
        self.avg_pts = self.total_pts / self.NUM_TEAMS
        self.avg_fg = self.total_fgm / self.total_fga
        self.avg_ft = self.total_ftm / self.total_fta

    def update_costs(self):
        for player in self.player_dict.values():
            player.update_cost(self.total_threes, self.total_reb, self.total_ast, self.total_stl, self.total_blk, self.total_pts, self.total_money_remaining)


    def ILPsolve(self, num_categories_win = 9, start_percent = 1.2, end_percent = 1.1, percent_decrease = 0.05):
        both_fg_ft = self.ILPsolve_helper(num_categories_win, start_percent, start_percent, end_percent, percent_decrease, 1, 1)
        #fg = self.ILPsolve_helper(num_categories_win, start_percent, start_percent, end_percent, percent_decrease, 1, 0)
        #ft = self.ILPsolve_helper(num_categories_win, start_percent, start_percent, end_percent, percent_decrease, 0, 1)
        #no_fg_ft = self.ILPsolve_helper(num_categories_win, start_percent, start_percent, end_percent, percent_decrease, 0, 0)

    def ILPsolve_helper(self, num_categories_win, start_percent, curr_percent, end_percent, percent_decrease, fg_switch, ft_switch):
        num_categories = self.NUM_CATEGORIES - 2

        if num_categories_win + fg_switch + ft_switch < 5:
            print('LOL you lost')
            return None# needs to be implemented

        players_chosen = []
        # https://www.coin-or.org/PuLP/pulp.html
        model = pulp.LpProblem("PickTeam maximizing problem", pulp.LpMaximize)

        # variables to help code
        category_list = ["THREES", "REB", "AST", "STL", "BLK", "PTS"]
        var_list1 = [self.my_threes, self.my_reb, self.my_ast, self.my_stl, self.my_blk, self.my_pts]
        var_list2 = [self.avg_threes, self.avg_reb, self.avg_ast, self.avg_stl, self.avg_blk, self.avg_pts]

        # Variables
        player_status = pulp.LpVariable.dicts("player_status", (name for name in self.player_dict.keys()), cat='Binary')    # 0 if player is taken, 1 if player is not taken
        category_status = pulp.LpVariable.dicts("category_status", (i for i in range(num_categories)), cat = 'Binary') # 0 if category in not taken, 1 if category is taken
        category_val = pulp.LpVariable.dicts("category_val", (i for i in range(num_categories)), cat = 'Continuous') # value of category

        
        # Objective
        model += pulp.lpSum([category_val[i] for i in range(num_categories)])   # maximize team

        # Constraints
        # keep track of category_val for threes, reb, ast, stl, blk, pts
        for i in range(len(category_list)):
            model += category_val[i] == (pulp.lpSum(player_status[name] * getattr(self.player_dict[name], category_list[i]) for name in self.player_dict.keys()) + var_list1[i]) / var_list2[i]

        # keep track of category_val for to
        model += category_val[6] == 2 - ((pulp.lpSum([player_status[name] * self.player_dict[name].TO for name in self.player_dict.keys()]) + self.my_to) / self.avg_to)

        # keep track of category_val for fg%
        RHS_fg = self.avg_fg * (1 + (0.5 * (curr_percent - 1)))
        RHS_ft = self.avg_ft * (1 + (0.5 * (curr_percent - 1)))  
        if fg_switch:
            model += pulp.LpFractionConstraint(numerator = (self.my_fgm + pulp.lpSum(player_status[name] * self.player_dict[name].FGM for name in self.player_dict.keys())), 
                denominator = (self.my_fga + pulp.lpSum(player_status[name] * self.player_dict[name].FGA for name in self.player_dict.keys())), sense = LpConstraintGE, RHS = RHS_fg)
        # keep track of category_val for ft%
        if ft_switch:
            model += pulp.LpFractionConstraint(numerator = (self.my_ftm + pulp.lpSum(player_status[name] * self.player_dict[name].FTM for name in self.player_dict.keys())), 
                denominator = (self.my_fta + pulp.lpSum(player_status[name] * self.player_dict[name].FTA for name in self.player_dict.keys())), sense = LpConstraintGE, RHS = RHS_ft)
        

        # make sure that for chosen categories team is at least x% better than avg
        for i in range(num_categories):
            model += category_val[i] >= curr_percent * category_status[i]  # make sure that for chosen categories, team is at least 5% better than avg
        # make sure don't overspend on players
        model += pulp.lpSum([player_status[name] * self.player_dict[name].cost for name in self.player_dict.keys()]) <= self.my_money_remaining
        # make sure fill up all spots left on team
        model += pulp.lpSum([player_status[name] for name in self.player_dict.keys()]) == self.my_spots_remaining
        # only try to win as many categories as set to
        model += pulp.lpSum([category_status[i] for i in range(num_categories)]) == num_categories_win

        model.solve()
        print(LpStatus[model.status])
        # print(findLHSValue(model))
        if pulp.LpStatus[model.status] == "Optimal":
            total_cost = 0  # used for testing purposes to make sure our total cost is less than my_money_remaining
            fgm = 0
            fga = 0
            ftm = 0
            fta = 0
            for name in self.player_dict.keys():
                if player_status[name].varValue == 1:
                    players_chosen.append(name)
                    print("Names:" + str(name))
                    fgm += self.player_dict[name].FGM
                    fga += self.player_dict[name].FGA
                    ftm += self.player_dict[name].FTM
                    fta += self.player_dict[name].FTA
                    total_cost += self.player_dict[name].cost
            for i in range(num_categories):
                print(category_val[i].varValue)
            fg_obtained = ((self.my_fgm + fgm) / (self.my_fga + fga)) / self.avg_fg
            ft_obtained = ((self.my_ftm + ftm) / (self.my_fta + fta)) / self.avg_ft
            print("fg%: " + str(fg_obtained))
            print("ft%: " + str(ft_obtained))


            print('Num_categories: ' + str(num_categories_win + fg_switch + ft_switch))
            print('curr_percent: ' + str(curr_percent))
            print("total_cost" + str(total_cost))
            print("sum:" + str(pulp.lpSum(category_val[i].varValue for i in range(num_categories)) + fg_obtained + ft_obtained))
            return players_chosen
        else:
            print('oh no')
            if curr_percent <= end_percent:
                return self.ILPsolve_helper(num_categories_win - 1, start_percent, start_percent, end_percent, percent_decrease, fg_switch, ft_switch)
            else:
                return self.ILPsolve_helper(num_categories_win, start_percent, curr_percent - percent_decrease, end_percent, percent_decrease, fg_switch, ft_switch)
          
    def choose_player(self, mine, name, cost):
        if mine == True: # if the player is on my team
            self.my_spots_remaining -= 1
            self.my_money_remaining -= cost
            self.my_threes += self.player_dict[name].THREES
            self.my_reb += self.player_dict[name].REB
            self.my_ast += self.player_dict[name].AST
            self.my_stl += self.player_dict[name].STL
            self.my_blk += self.player_dict[name].BLK
            self.my_to += self.player_dict[name].TO
            self.my_pts += self.player_dict[name].PTS
            self.my_fgm += self.player_dict[name].FGM
            self.my_fga += self.player_dict[name].FGA
            self.my_ftm += self.player_dict[name].FTM
            self.my_fta += self.player_dict[name].FTA

        self.total_money_remaining -= cost
        self.player_dict.pop(name)


    # reads input and creates all_players
    def read_input(self, filename):
        #global player_dict
        with open(filename) as f:
            for i in range(self.SPOTS_ALL_TEAMS):
                stats = ast.literal_eval(f.readline())
                name = stats[0]
                # print(name)
                new_player = Player(float(stats[1]), float(stats[2]), float(stats[3]), float(stats[4]), float(stats[5]), 
                    float(stats[6]), float(stats[7]), float(stats[8]), float(stats[9]), float(stats[10]), float(stats[11]), 
                    float(stats[12]), float(stats[13]), float(stats[14]), float(stats[15]))
                self.player_dict[name] = new_player
          



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimizing Team")
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()
    game = Game()
    print(game.SPOTS_ALL_TEAMS)
    game.read_input(args.input_file) # read inputs
    game.recompute_totals() #compute totals of all categories
    game.compute_team_averages() #with totals compute team averages
    game.update_costs()  #update every player's costs
    game.player_dict['Goran Dragic'].update_cost(game.total_threes, game.total_reb, game.total_ast, game.total_stl, game.total_blk, game.total_pts, game.total_money_remaining)
    print(game.player_dict['Goran Dragic'].FTM)
    print(game.player_dict['Goran Dragic'].FTA)
    #print(game.my_spots_remaining)
    #print(game.avg_blk)
    #print(game.my_threes)
    print(game.avg_ft)
    print(game.avg_fg)
    game.ILPsolve()
    # game.choose_player(True, 'Goran Dragic', 99)   # continuously choose_player, recompute_totals, update_costs(), and ILPsolve. Repeat.
    #print(game.my_threes)
    #print(game.my_money_remaining)
    #print(game.my_spots_remaining)



      # items_chosen = solve(P, M, N, C, items, constraints)
      # write_output(args.output_file, items_chosen)
