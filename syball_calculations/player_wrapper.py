

class Player:

	def __init__(self, GP, FG, FT, Threes, REB, AST, STL, BLK, TO, PTS):
		self.GP = GP
		self.FG = FG
		self.FT = FT
		self.Threes = Threes
		self.REB = REB
		self.AST = AST
		self.STL = STL
		self.BLK = BLK
		self.TO = TO
		self.PTS = PTS
		self.cost = 0

	def update_cost(self, total_threes, total_reb, total_ast, total_stl, total_blk, total_pts, money):
		"""num_categories = 6
		cost_threes = (self.Threes/total_threes)
		print(cost_threes)
		print(self.Threes)
		print(total_threes)
		cost_reb = (self.REB/total_reb)
		print(cost_reb)
		cost_ast = (self.AST/total_ast)
		print(cost_ast)
		cost_stl = (self.STL/total_stl)
		print(cost_stl)
		cost_blk = (self.BLK/total_reb)
		print(cost_blk)
		cost_pts= (self.PTS/total_pts)
		print(cost_pts)
		avg_cost = (cost_threes + cost_reb + cost_ast + cost_stl + cost_blk + cost_pts) / num_categories
		print(avg_cost)
		cost = avg_cost * money
		print(cost)"""
		self.cost = self.cost



