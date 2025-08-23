import struct
import json
import random
import time

from utils import *


# --- basic bot ---
class Bot:
	def __init__(self, bot_id, game_type = "card_game"):
		self.bot_id = bot_id
		self.name = f"Bot_{bot_id}"
		self.game_type = game_type


	# returns a move from available_moves based on the game_state
	def move(self, game_state, available_moves):
		time.sleep(random.uniform(0.5, 1.5))

		if not available_moves:
			return None

		return random.choice(available_moves)


	def eval_game_state(self, game_state):
		pass


# # --- specialised bot classes ---
# class SmartBot(Bot):
# 	def move(self, game_state, available_moves):
# 		time.sleep(random.uniform(1.0, 2.0))

# 		if not available_moves:
# 			return None

# 		# prefer higher-value cards
# 		# if logic fails, fallback to random
# 		return random.choice(available_moves)


# class MLBot(Bot):
# 	def __init__(self, bot_id, model_path = None):
# 		super().__init__(bot_id)
# 		self.model = self.load_model(model_path) if model_path else None


# 	# returns model from model_path file
# 	def load_model(self, model_path):
# 		return None


# 	def move(self, game_state, available_moves):
# 		if self.model and available_moves:
# 			# convert game state to features and use model to predict best move
# 			# predicted_move = self.model.predict(features)
# 			# return predicted_move
# 			pass

# 		# fallback to random if no model or prediction fails
# 		return random.choice(available_moves) if available_moves else None
