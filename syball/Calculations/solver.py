import argparse
import ast
from playerWrapper import Player

#fixed
PLAYERS_PER_TEAM = 9
NUM_TEAMS = 16
MONEY_PER_TEAM = 200
SPOTS_ALL_TEAMS = PLAYERS_PER_TEAM * NUM_TEAMS #total number of players that need to be drafted


#changing
total_money_remaining = NUM_TEAMS * MONEY_PER_TEAM 
spots_remaining = 9  
money_remaining= 200  
player_dict = {}   #remaining players
my_threes = 0
my_reb = 0
my_ast = 0
my_stl = 0
my_blk = 0
my_to = 0
my_pts = 0
total_threes = 0
total_reb = 0
total_ast = 0
total_stl = 0
total_blk = 0
total_to = 0
total_pts = 0
"""avg_threes = 0
avg_reb = 0
avg_ast = 0
avg_stl = 0
avg_blk = 0
avg_to = 0
avg_pts = 0"""

def recompute_totals(): #recompute totals with remaining players left
  global total_threes
  global total_reb
  global total_ast 
  global total_stl
  global total_blk
  global total_to 
  global total_pts 

  total_threes = 0
  total_reb = 0
  total_ast = 0
  total_stl = 0
  total_blk = 0
  total_to = 0
  total_pts = 0
  for player in player_dict.values():
    total_threes += player.Threes
    total_reb += player.REB
    total_ast += player.AST
    total_stl += player.STL
    total_blk += player.BLK
    total_to += player.TO
    total_pts += player.PTS






def update_costs():
  global player_dict

  for player in player_dict.values():
    player.update_cost(total_threes, total_reb, total_ast, total_stl, total_blk, total_pts, total_money_remaining)





def solve():
  return

def choose_player(mine, name, cost):
  global my_threes
  global my_reb
  global my_ast 
  global my_stl
  global my_blk
  global my_to 
  global my_pts 
  global total_money_remaining
  global player_dict

  if mine == True: #if the player is on my team
    spots_remaining -= 1
    money_remaining -= cost
    my_threes += player_dict[name].Threes
    my_reb += player_dict[name].REB
    my_ast += player_dict[name].AST
    my_stl += player_dict[name].STL
    my_blk += player_dict[name].BLK
    my_to += player_dict[name].TO
    my_pts += player_dict[name].PTS
  total_money_remaining -= cost
  player_dict.pop(name)


#reads input and creates all_players
def read_input(filename):
  global total_threes
  global total_reb
  global total_ast 
  global total_stl
  global total_blk
  global total_to 
  global total_pts 
  global player_dict

  with open(filename) as f:
    for i in range(SPOTS_ALL_TEAMS):
      stats = ast.literal_eval(f.readline())
      name = stats[0]
      new_player = Player(float(stats[1]), float(stats[2]), float(stats[3]), float(stats[4]), float(stats[5]), 
        float(stats[6]), float(stats[7]), float(stats[8]), float(stats[9]), float(stats[10]))
      player_dict[name] = new_player

"""def compute_team_averages():
  global avg_threes 
  global avg_reb 
  global avg_ast
  global avg_stl
  global avg_blk
  global avg_to
  global avg_pts

  avg_threes = total_threes/NUM_TEAMS
  avg_reb = total_reb/NUM_TEAMS
  avg_ast = total_ast/NUM_TEAMS
  avg_stl = total_stl/NUM_TEAMS
  avg_blk = total_blk/NUM_TEAMS
  avg_to = total_to/NUM_TEAMS
  avg_pts = total_pts/NUM_TEAMS"""

  



if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Optimizing Team")
  parser.add_argument("input_file", type=str)
  args = parser.parse_args()
  read_input(args.input_file) #read inputs
  recompute_totals()

  player_dict['Goran Dragic'].update_cost(total_threes, total_reb, total_ast, total_stl, total_blk, total_pts, total_money_remaining)
  #update_costs() #first round of costs
  #print(total_money_remaining)
  #print(total_threes)
  print(player_dict['Goran Dragic'].cost)
  #print(player_dict)
  #solve()
  #choose_player(True, )


  



  #items_chosen = solve(P, M, N, C, items, constraints)
  #write_output(args.output_file, items_chosen)