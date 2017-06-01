from bs4 import BeautifulSoup as BS
import argparse

player_list = [] #list of all players
NUM_PAGES = 10

def extractor(): 
	page = 0
	for i in range(NUM_PAGES):
		with open("page" + str(page) + ".html") as fp:
			soup = BS(fp, "lxml")
		soup1 = soup.tbody
		for tbody in soup1.find_all('table'):
			new_player = []
			name = tbody.a.get_text()
			print(name)
			tr = tbody.find_all('tr')[2]
			stats = tr.find_all('td')
			stats = [stat.get_text() for stat in stats]
			new_player.append(name)
			new_player.append(stats[2])
			new_player.append(stats[4])
			new_player.append(stats[5])
			new_player.append(stats[6])
			new_player.append(stats[7])
			new_player.append(stats[8])
			new_player.append(stats[10])
			new_player.append(stats[11])
			new_player.append(stats[12])
			new_player.append(stats[13])
			player_list.append(new_player)
		page = page + 1
	#player_list.append(['Total', None, None, None, total_threes, total_reb, 
			#total_ast, total_stl, total_blk, total_to, total_pts])
	return player_list


def write_output(filename, player_list):
  with open(filename, "w") as f:
    for i in player_list:
      f.write("{0}\n".format(i))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Grabbing stats")
  parser.add_argument("output_file", type=str, help="____.out")
  args = parser.parse_args()
  all_players = extractor()
  write_output(args.output_file, all_players)


	


