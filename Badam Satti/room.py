import random


class Room:
	def __init__(self, num_players):
		self.num_players = num_players
		self.game_start = False
		self.finished = False

		# ref cards
		self.card_num = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
		self.card_suite = ['H', 'S', 'D', 'C']
		self.ref_cards = sum([[str(i) + s for i in self.card_num] for s in self.card_suite], [])

		# shuffle cards and distribute
		self.shuffled_cards = self.ref_cards.copy()		# not shuffled yet
		self.player_cards = []
		self.leftover_cards = []

		# setup the table and round
		self.table = []
		self.turn = random.choice(range(self.num_players))
		self.rank = []
		self.active_players = list(range(self.num_players))


	# sort cards in their (1st) card suite (2nd) card number 
	def sort_cards(self, cards):
		return sorted(cards, key=lambda x: self.card_suite.index(x[-1])*100+self.card_num.index(x[:-1]))


	# shuffle cards and distribute them among players & setup the table
	def initialise_board(self):
		random.shuffle(self.shuffled_cards)

		# distribute cards among players
		cards_per_player = len(self.ref_cards) // self.num_players
		cards_left = len(self.ref_cards) % self.num_players
		self.player_cards = [self.sort_cards(self.shuffled_cards[i * cards_per_player : i * cards_per_player + cards_per_player]) for i in range(self.num_players)]
		self.leftover_cards = self.shuffled_cards[len(self.ref_cards) - cards_left :]

		self.table = [(-1, -1) for _ in self.card_suite]
		self.find_7H()


	# find player with 7H card, place all '7' leftover cards on the table
	def find_7H(self):
		for i, cards in enumerate(self.player_cards):
			if '7H' in cards:
				self.turn = i
		for si in range(len(self.card_suite)):
			c = self.ref_cards[si * 13 + 6]
			if c in self.leftover_cards:
				self.place_card(si * 13 + 6)
				self.leftover_cards.remove(c)


	# find list of all possible card moves of the player_id
	def possible_moves(self, player_id):
		if not self.game_start:
			return ['7H']
		moves = []
		for si, (l, r) in enumerate(self.table):
			if l == -1:
				moves.append(self.ref_cards[si * 13 + 6])
				continue
			if l != 0:
				moves.append(self.ref_cards[si * 13 + l - 1])
			if r != 12:
				moves.append(self.ref_cards[si * 13 + r + 1])
		return [c for c in moves if c in self.player_cards[player_id]]


	# places card on the table, check for leftover cards simultaneously
	def place_card(self, move):
		if move == "7H":
			self.game_start = True
		ci = self.ref_cards.index(move)
		n, s = ci % 13, ci // 13		# extract card number + suite number
		l, r = self.table[s] if self.table[s][0] != -1 else (n, n)
		l = n if n == l - 1 else l
		r = n if n == r + 1 else r 
		while l > 0 and (self.ref_cards[s * 13 + l - 1] in self.leftover_cards):		# decrement till leftover cards are placed
			self.leftover_cards.remove(self.ref_cards[s * 13 + l - 1])
			l -= 1
		while r < 12 and (self.ref_cards[s * 13 + r + 1] in self.leftover_cards):		# increament till leftover cards are placed
			self.leftover_cards.remove(self.ref_cards[s * 13 + r + 1])
			r += 1
		self.table[s] = (l, r)
		self.player_cards[self.turn].remove(move)


	# update rank, active players, turn
	def update_state(self):
		if self.turn in self.active_players:
			if self.player_cards[self.turn] == []:
				self.rank.append(self.turn)
				self.active_players.remove(self.turn)

		# check for game over
		if self.active_players == []:
			self.finished = True

		self.turn = (self.turn + 1) % self.num_players
		while (self.active_players != []) and (self.turn not in self.active_players):
			self.turn = (self.turn + 1) % self.num_players


	# package game state for the client
	def serialize(self, player_id):
		data = {
				"turn": self.turn,		# who's turn is it?
				"my_turn": 1 if (player_id == self.turn) else 0,		# is it my turn?
				"table": self.table, 		# cards put on the table
				"num_cards": [len(p) for p in self.player_cards],		# number of cards with each player
				"my_cards": self.player_cards[player_id],		# my cards left
				"leftover_cards": self.leftover_cards,		# cards left to be dealt
				}
		return data


	# verify if the card move is valid or not (update the game state if valid)
	def verify_move(self, player_id, move):
		move = move.upper()
		valid = False
		if player_id == self.turn:		# acceptable player_id and move
			allowed_moves = self.possible_moves(player_id)
			if allowed_moves == []:
				valid = (move == "PASS")
			else:
				valid = (move in allowed_moves)

		if valid:
			if move != "PASS":
				self.place_card(move)
			self.update_state()
		return valid


	# send current status of leaderboard (i.e, rank + score)
	def leaderboard(self):
		return self.rank