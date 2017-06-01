#!/usr/bin/env python

from __future__ import division
from pulp import * 
from collections import defaultdict #http://stackoverflow.com/questions/960733/python-creating-a-dictionary-of-lists



"""
===============================================================================
  Please complete the following function.
===============================================================================
"""
temp_class_names = []     #delete this later, this is to check if class constraints break

def solve(P, M, N, C, items, constraints):
  """
  Write your amazing algorithm here.

  Return: a list of strings, corresponding to item names.
  """
  items = [x for x in items if x[4] > x[3] if x[3] <= M if x[2] <= P]   #remove items that have higher cost than resale cost
  N = len(items) #update N
  item_names = []
  class_names = defaultdict(list)  #remember items that are part of the same class
  weights = []
  costs = []
  resale_values = []
  item_index = 0
  for item in items:
    item_names.append(item[0])
    class_names[item[1]].append(item_index)
    temp_class_names.append(item[1])    #delete this later, this is to check if class constraints break
    weights.append(item[2])
    costs.append(item[3])
    resale_values.append(item[4])
    item_index += 1


  
  return LPSolver(P, M, N, C, constraints, item_names, class_names, weights, costs, resale_values)


def LPSolver(P, M, N, C, constraints, item_names, class_names, weights, costs, resale_values):
  items_bought = []

  class_set = set()  #delete this later, this is to check if class constraints break


  #https://www.coin-or.org/PuLP/pulp.html

  model = pulp.LpProblem("PickItems maximizing problem", pulp.LpMaximize)



  #Variables
  item_status = pulp.LpVariable.dicts("item_status", (i for i in range(N)), cat='Binary')    #0 if item is taken, 1 if item is not taken
  class_status = pulp.LpVariable.dicts("class_status", (key for key in class_names.keys()), cat = 'Binary') #0 if items in class are not taken, 1 if items in class are taken


  #Objective
  model += M + pulp.lpSum([(item_status[i] * resale_values[i]) - (item_status[i]*costs[i]) for i in range(N)])    #maximize remaining money + profit

  #Constraints
  model += pulp.lpSum([item_status[i] * weights[i] for i in range(N)]) <= P #make sure total weight < P
  model += pulp.lpSum([item_status[i] * costs[i] for i in range(N)]) <= M   #make sure total cost < M

  #write y-class constraints
  for key in class_names.keys():
    if len(class_names[key]) == 1:   #only one item item in the class
      model += class_status[key] == item_status[class_names[key][0]]
    else:
      model+= class_status[key] <= pulp.lpSum([item_status[i] for i in class_names[key]])
      for i in range(len(class_names[key])):
        model += class_status[key] >= item_status[class_names[key][i]]
  
  #deal with the constraints
  for i in range(C):
    for incompatible_class in list(constraints[i]):
      if incompatible_class not in class_names:     #if none of the items have this class
        constraints[i].remove(incompatible_class)
    model += pulp.lpSum(class_status[j] for j in constraints[i]) <= 1


  model.solve()
  total_weight = 0  #used for testing purposes to make sure our total weight is less than P
  total_cost = 0  #used for testing purposes to make sure our total cost is less than M
  for i in range(N):
    if item_status[i].varValue == 1:
      items_bought.append(item_names[i])

      class_set.add(temp_class_names[i])   #delete this later, this is to check if class constraints break

      total_weight += weights[i]
      total_cost += costs[i]
  
  items_bought.append(pulp.value(model.objective))
  

  print(pulp.LpStatus[model.status])

  #Double check total_weight 
  if total_weight > P:
    print("Weight broken")
    items_bought.append(total_weight)

  #Double check total_cost
  if total_cost > M:
    print("Cost broken")
    items_bought.append(total_cost)

  #Double check conflicts in constraints
  for i in range(C):
    seen_class = None
    seen = False
    for item_class in constraints[i]:
      if item_class in class_set:
        if (seen == False):
          seen_class = item_class
          seen = True
        else:
          print("Constraints broken")
          items_bought.append("Constraint conflict")
          items_bought.append(seen_class)
          items_bought.append(item_class)

  #print(class_set)
  #print(len(class_set))
  return items_bought