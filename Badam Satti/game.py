import sys

import pygame


class Game:
	def __init__(self, width = 700, height = 600):
		self.width = width
		self.height = height
		self.player_names = []

		# setup reference cards
		self.card_num = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
		self.card_suite = ['H', 'S', 'D', 'C']
		self.ref_cards = sum([[str(i) + s for i in self.card_num] for s in self.card_suite], [])
		
		pygame.init()
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.clock = pygame.time.Clock()
		self.font = pygame.font.Font(size = self.width // 20)

		# board dimensions
		self.step_size = min(self.width, self.height)/27		# standard distance used to design the board
		self.card_size = (self.step_size * 3, self.step_size * 4)		# dimensions of card on the table
		self.row_step = (self.step_size * 1.5, self.step_size * 5)		# step size of rows in (x, y) direction
		self.row_centers = [(self.step_size * 2.5, self.step_size * 3 + self.row_step[1] * i) for i in range(4)]		# starting position of suite rows
		self.table_height = self.row_centers[-1][1] + self.step_size * 3
		self.hover_scale = 0.1  		# scaling factor when hover over it 
		self.color_scale = 0.95			# lighten color by this scale

		# game state
		self.turn = 0 			# who's turn is it?
		self.my_turn = 0 		# is it my turn?
		self.table = []			# config of the table
		self.num_cards = []			# number of cards each player has
		self.my_cards = []			# user selects a card from here
		self.leftover_cards = []		# cards left to be dealt

		# event handling
		self.clicked = False		# clicked on any card
		self.finished = False		# game over (display rank)
		self.close = False
		self.rank = []
		self.mouse_pos = None
		self.move = ""


	# setting up the game env
	def setup_game(self, data):
		self.player_names = data


	# unpack the game state
	def deserialize(self, data):
		self.turn = data.get("turn")
		self.my_turn = data.get("my_turn")
		self.table = data.get("table")
		self.num_cards = data.get("num_cards")
		self.my_cards = data.get("my_cards")
		self.leftover_cards = data.get("leftover_cards")
				

	# keyboard or mouse events
	def handle_events(self):
		self.clicked = False
		self.mouse_pos = pygame.mouse.get_pos()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.close = True
				pygame.quit()
				# sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					self.clicked = True

		return self.close


	# draw waiting lobby / loading
	def draw_waiting(self):
		text = "WAITING FOR PLAYERS ..."
		self.screen.blit(self.font.render(text, True, (0, 0, 0)), (self.step_size, self.step_size + self.table_height))


	# sends "PASS" to client for making a move
	def selected_pass(self):
		self.move = "PASS"


	# place card at the space_center
	def draw_card(self, card, space_center, selectable = False):
		if card is None:
			card = "0_GREY"
		card_img = pygame.image.load(f"assets/{card}.png").convert_alpha()
		hover = False
		if selectable:
			# create a bounding box for mouse hover
			mouse_rect = pygame.Rect(space_center[0] - self.card_size[0] / 2, space_center[1] - self.card_size[1] / 2, self.card_size[0] / 2, self.card_size[1])
			if mouse_rect.collidepoint(self.mouse_pos):
				hover = True
				if self.clicked:
					# sends selected card to client for making a move
					self.move = card
		target_rect = pygame.Rect(space_center[0] - (self.card_size[0] / 2) * (1 + hover * self.hover_scale), space_center[1] - (self.card_size[1] / 2) * (1 + hover * self.hover_scale), self.card_size[0] * (1 + hover * self.hover_scale), self.card_size[1] * (1 + hover * self.hover_scale))
		scaled_card_img = pygame.transform.scale(card_img, target_rect.size)
		self.screen.blit(scaled_card_img, target_rect)


	# button with text, color, position (x, y), dimensions (w, h), action
	def draw_button(self, text, color, pos, dim, action):
		button_rect = pygame.Rect(pos[0], pos[1], dim[0], dim[1])

		if button_rect.collidepoint(self.mouse_pos):
			# darken color
			pygame.draw.rect(self.screen, color, button_rect)
			if self.clicked:
				action()
		else:
			# lighten color
			pygame.draw.rect(self.screen, tuple(c * self.color_scale for c in color), button_rect)

		text_surf = self.font.render(text, True, (0, 0, 0))
		text_rect = text_surf.get_rect()
		text_rect.center = button_rect.center 			# align centers of text and button
		self.screen.blit(text_surf, text_rect)


	# draw the game board / table
	def draw_board(self, end_screen):
		# draw suite cards on the table
		for i, (l, r) in enumerate(self.table):
			if l == -1:
				l, r = 1, 0
			self.draw_card(None, (self.row_centers[i][0] + self.row_step[0] * 6, self.row_centers[i][1]))
			for j in range(l, r + 1):
				self.draw_card(self.ref_cards[i * 13 + j], (self.row_centers[i][0] + self.row_step[0] * j, self.row_centers[i][1]))

		# draw my cards
		for i, card in enumerate(self.my_cards):
			space_center = (self.row_centers[-1][0] + self.row_step[0] * i, self.row_centers[-1][1] + self.step_size * 6)
			self.draw_card(card, space_center, selectable = True)
		
		# draw PASS button
		button_pos = (self.width - self.step_size * 4, self.row_centers[-1][1] + self.step_size * 5)
		self.draw_button("PASS", pygame.Color("burlywood4"), button_pos, (self.step_size * 3, self.step_size * 2), self.selected_pass)

		# draw leftover cards
		leftover_pos = (self.row_centers[2][0] + self.row_step[0] * 13 + self.step_size * 3, self.row_centers[2][1])
		self.draw_card(None, leftover_pos)
		for i, card in enumerate(self.leftover_cards):
			space_center = (leftover_pos[0], leftover_pos[1] + self.step_size * i)
			self.draw_card(card, space_center)

		# display leaderboard
		text_start = (self.row_centers[0][0] + self.row_step[0] * 13 + self.step_size, self.row_centers[0][1])
		for i, p in enumerate(self.player_names):
			text = f"{'>' if self.turn == i else ''} {p} -> {self.num_cards[i]}"
			if end_screen:
				text = f"{p} -> {self.rank.index(i) + 1} {'(W)' if self.rank.index(i) == 0 else ''}"
			self.screen.blit(self.font.render(text, True, (0, 0, 0)), (text_start[0], text_start[1] + self.step_size * i))


	# draw the entire screen (waiting + board)
	def draw(self, started = True, end_screen = False):
		self.move = ""

		if not self.close:
			self.screen.fill((97, 200, 86))			# green table cloth
			pygame.draw.rect(self.screen, (216, 153, 70), (0, self.table_height, self.width, self.height - self.table_height), 0)		# player selection area
			if not started:
				self.draw_waiting()
			else:
				self.draw_board(end_screen)
			pygame.display.update()
			self.clock.tick(10)		# arg = FPS (frames per sec)

		return self.move


	# game ended, so display results
	def update_results(self, data):
		self.rank = data
		self.finished = True


	# after the game is over (display leaderboard)
	def handle_end(self):
		if not self.close:
			flag = True
			while flag and (not self.close):
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						self.close = True
						flag = False

				# display end screen + rank
				self.draw(end_screen = True)

			pygame.quit()
