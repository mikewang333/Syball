import argparse
import ast
from player_wrapper import Player
from pulp import * 

#from integer_program import LPSolver 

#fixed
PLAYERS_PER_TEAM = 9
NUM_TEAMS = 16
NUM_CATEGORIES = 9
MONEY_PER_TEAM = 200
SPOTS_ALL_TEAMS = PLAYERS_PER_TEAM * NUM_TEAMS #total number of players that need to be drafted


#changing
global total_money_remaining
global my_spots_remaining 
global my_money_remaining
global player_dict

global my_threes
global my_reb
global my_ast
global my_stl
global my_blk
global my_to
global my_pts
global my_fgm
global my_fga
global my_ftm
global my_fta


global total_threes
global total_reb
global total_ast
global total_stl
global total_blk
global total_to
global total_pts
global total_fgm
global total_fga
global total_ftm
global total_fta

global avg_threes
global avg_reb
global avg_ast
global avg_stl
global avg_blk
global avg_to
global avg_pts
global avg_fg
global avg_ft

#gives value to all variables
def initialize():
  global total_money_remaining
  global my_spots_remaining 
  global my_money_remaining
  global player_dict
  global my_threes
  global my_reb
  global my_ast
  global my_stl
  global my_blk
  global my_to
  global my_pts
  global my_fgm
  global my_fga
  global my_ftm
  global my_fta
  global total_threes
  global total_reb
  global total_ast
  global total_stl
  global total_blk
  global total_to
  global total_pts
  global total_fgm
  global total_fga
  global total_ftm
  global total_fta
  global avg_threes
  global avg_reb
  global avg_ast
  global avg_stl
  global avg_blk
  global avg_to
  global avg_pts
  global avg_fg
  global avg_ft

  total_money_remaining = NUM_TEAMS * MONEY_PER_TEAM 
  my_spots_remaining = PLAYERS_PER_TEAM
  my_money_remaining = MONEY_PER_TEAM
  player_dict = {}
  my_threes = 0
  my_reb = 0
  my_ast = 0
  my_stl = 0
  my_blk = 0
  my_to = 0
  my_pts = 0
  my_fgm = 0
  my_fga = 0
  my_ftm = 0
  my_fta = 0
  total_threes = 0
  total_reb = 0
  total_ast = 0 
  total_stl = 0
  total_blk = 0
  total_to = 0
  total_pts = 0
  total_fgm = 0
  total_fga = 0
  total_ftm = 0
  total_fta = 0
  avg_threes = 0
  avg_reb = 0
  avg_ast = 0
  avg_stl = 0
  avg_blk = 0
  avg_to = 0
  avg_pts = 0
  avg_fg = 0
  avg_ft = 0




#gives total counts for all stats in player_dict
def recompute_totals():
  global total_threes
  global total_reb
  global total_ast
  global total_stl
  global total_blk
  global total_to
  global total_pts
  global total_fgm
  global total_fga
  global total_ftm
  global total_fta

  total_threes = 0
  total_reb = 0
  total_ast = 0
  total_stl = 0
  total_blk = 0
  total_to = 0
  total_pts = 0
  total_fgm = 0
  total_fga = 0
  total_ftm = 0
  total_fta = 0
  

  for player in player_dict.values():
    total_threes += player.Threes
    total_reb += player.REB
    total_ast += player.AST
    total_stl += player.STL
    total_blk += player.BLK
    total_to += player.TO
    total_pts += player.PTS
    total_fgm += player.FGM
    total_fga += player.FGA
    total_ftm += player.FTM
    total_fta += player.FTA

#compute team averages
def compute_team_averages():
  global avg_threes
  global avg_reb 
  global avg_ast
  global avg_stl
  global avg_blk
  global avg_to 
  global avg_pts
  global avg_fg
  global avg_ft

  avg_threes = total_threes/NUM_TEAMS
  avg_reb = total_reb/NUM_TEAMS
  avg_ast = total_ast/NUM_TEAMS
  avg_stl = total_stl/NUM_TEAMS
  avg_blk = total_blk/NUM_TEAMS
  avg_to = total_to/NUM_TEAMS
  avg_pts = total_pts/NUM_TEAMS
  avg_fg = total_fgm/total_fga
  avg_ft = total_ftm/total_fta


def update_costs():
  global player_dict
  for player in player_dict.values():
    player.update_cost(total_threes, total_reb, total_ast, total_stl, total_blk, total_pts, total_money_remaining)


def ILPsolve(num_categories_win):
  players_chosen= []
  #https://www.coin-or.org/PuLP/pulp.html
  model = pulp.LpProblem("PickTeam maximizing problem", pulp.LpMaximize)

  #variables to help code
  category_list = ["Threes", "REB", "AST", "STL", "BLK", "PTS"]
  var_list1 = [my_threes, my_reb, my_ast, my_stl, my_blk, my_pts]
  var_list2 = [avg_threes, avg_reb, avg_ast, avg_stl, avg_blk, avg_pts]

  #Variables
  player_status = pulp.LpVariable.dicts("player_status", (name for name in player_dict.keys()), cat='Binary')    #0 if player is taken, 1 if player is not taken
  category_status = pulp.LpVariable.dicts("category_status", (i for i in range(NUM_CATEGORIES)), cat = 'Binary') #0 if category in not taken, 1 if category is taken
  category_val = pulp.LpVariable.dicts("category_val", (i for i in range(NUM_CATEGORIES)), cat = 'Continuous') #value of category
  y = pulp.LpVariable.dicts("y", (name for name in player_dict.keys()), cat='Continuous')
  #t = pulp.LpVariable.dicts("t", (name for name in player_dict.keys()), cat='Continuous')
  
  #Objective
  model += pulp.lpSum([category_val[i] for i in range(NUM_CATEGORIES)])   #maximize team

  #Constraints
  #keep track of category_val for threes, reb, ast, stl, blk, pts
  for i in range(len(category_list)):
    model += category_val[i] == (pulp.lpSum(player_status[name] * getattr(player_dict[name], category_list[i]) for name in player_dict.keys()) + var_list1[i]) / var_list2[i]

  #keep track of category_val for fg%
  """for name in player_dict.keys():
    model += y[name] == int(player_status[name] / (player_dict[name].FGA * player_status[name] + my_fga))
  model += category_val[6] == pulp.lpSum(player_dict[name].FGM * y[name] for name in player_dict.keys())
  model += pulp.lpSum(player_dict[name].FGA * y[name] for name in player_dict.keys()) == 1"""
  #y = pulp.lpDot(player_status, 1 / (pulp.lpSum([player_status[name] * player_dict[name].FGA for name in player_dict.keys()]) + my_fga))
  #t = 1 / (pulp.lpSum([player_status[name] * player_dict[name].FGA for name in player_dict.keys()]) + my_fga)
  #model += category_val[6] == pulp.lpSum([y * player_status[name] for name in player_dict.keys()]) + (my_fgm * t)
  #model += pulp.lpSum([y * my_fgm]) + my_fga*t == 1
  
  #HELP ME ON WORKING MODEL 
  model += category_val[6] == 0.8
  model += category_val[7] == 0.8


  #model += category_val[6] == pulp.lpSum([player_status[name] / player_status[name] for name in player_dict.keys()])
  #model += category_val[6] == ((my_fgm + pulp.lpSum([player_status[name] * player_dict[name].FGM for name in player_dict.keys()])) / (my_fga + pulp.lpSum([player_status[name] * player_dict[name].FGA for name in player_dict.keys()]))) / avg_fg

  #keep track of category_val for ft%
  #model += category_val[7] * avg_ft * (my_fta + pulp.lpSum([player_status[name] * player_dict[name].FTA for name in player_dict.keys()])) == my_ftm + pulp.lpSum([player_status[name] * player_dict[name].FTM for name in player_dict.keys()])

  #keep track of category_val for to
  model += category_val[8] == 2 - ((pulp.lpSum([player_status[name] * player_dict[name].TO for name in player_dict.keys()]) + my_to) / avg_to)

  #make sure that for chosen categories team is at least 5% better than avg
  for i in range(NUM_CATEGORIES):
    model += category_val[i] >= 1.3 * category_status[i]  #make sure that for chosen categories, team is at least 5% better than avg
    """if category_val[i] >= 1.1: make sure that for chosne categories, team is capped at 10 better than avg (any better and it doesn't matter)
       category_val[i] = 1.1""" 
  #make sure don't overspend on players
  model += pulp.lpSum([player_status[name] * player_dict[name].cost for name in player_dict.keys()]) <= my_money_remaining
  #make sure fill up all spots left on team
  model += pulp.lpSum([player_status[name] for name in player_dict.keys()]) == my_spots_remaining
  #only try to win as many categories as set to
  model += pulp.lpSum([category_status[i] for i in range(NUM_CATEGORIES)]) == num_categories_win

  model.solve()

  print(pulp.LpStatus[model.status])
  if pulp.LpStatus[model.status] == "Optimal":
    total_cost = 0  #used for testing purposes to make sure our total cost is less than my_money_remaining
    for name in player_dict.keys():
      if player_status[name].varValue == 1:
        players_chosen.append(name)
        print("Names:" + str(name))
        total_cost += player_dict[name].cost
    for i in range(NUM_CATEGORIES):
      print(category_val[i].varValue)
    print('Num_categories: ' + str(num_categories_win))
    print("total_cost" + str(total_cost))
    return players_chosen
  else:
    print('oh no')
    return ILPsolve(num_categories_win - 1)
    



def choose_player(mine, name, cost):
  global total_money_remaining 
  global my_spots_remaining
  global my_money_remaining
  global player_dict

  global my_threes
  global my_reb
  global my_ast
  global my_stl 
  global my_blk
  global my_to
  global my_pts
  global my_fgm
  global my_fga
  global my_ftm
  global my_fta


  if mine == True: #if the player is on my team
    my_spots_remaining -= 1
    my_money_remaining -= cost
    my_threes += player_dict[name].Threes
    my_reb += player_dict[name].REB
    my_ast += player_dict[name].AST
    my_stl += player_dict[name].STL
    my_blk += player_dict[name].BLK
    my_to += player_dict[name].TO
    my_pts += player_dict[name].PTS
    my_fgm += player_dict[name].FGM
    my_fga += player_dict[name].FGA
    my_ftm += player_dict[name].FTM
    my_fta += player_dict[name].FTA

  total_money_remaining -= cost
  player_dict.pop(name)


#reads input and creates all_players
def read_input(filename):
  global player_dict
  with open(filename) as f:
    for i in range(SPOTS_ALL_TEAMS):
      stats = ast.literal_eval(f.readline())
      name = stats[0]
      print(name)
      new_player = Player(float(stats[1]), float(stats[2]), float(stats[3]), float(stats[4]), float(stats[5]), 
        float(stats[6]), float(stats[7]), float(stats[8]), float(stats[9]), float(stats[10]), float(stats[11]), 
        float(stats[12]), float(stats[13]), float(stats[14]), float(stats[15]))
      player_dict[name] = new_player
  



if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Optimizing Team")
  parser.add_argument("input_file", type=str)
  args = parser.parse_args()
  initialize()
  read_input(args.input_file) #read inputs
  recompute_totals()
  compute_team_averages()
  update_costs()
  #solve()
  player_dict['Goran Dragic'].update_cost(total_threes, total_reb, total_ast, total_stl, total_blk, total_pts, total_money_remaining)
  #update_costs() #first round of costs
  print(player_dict['Goran Dragic'].FTM)
  print(player_dict['Goran Dragic'].FTA)
  #choose_player(True, 'Goran Dragic', 99)   #continuously choose_player, recompute_totals, update_costs(), solve
  #recompute_totals()
  #update_costs()
  #print(my_spots_remaining)
  #print(avg_blk)
  #print(my_threes)
  #print(avg_ft)
  print(avg_ast)
  print(avg_ft)
  ILPsolve(10)
  #choose_player(True, )


  



  #items_chosen = solve(P, M, N, C, items, constraints)
  #write_output(args.output_file, items_chosen)