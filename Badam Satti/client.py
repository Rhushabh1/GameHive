import socket
import threading
import json
import struct
import time

from protocols import Protocols
from game import Game


class Client:
	def __init__(self, host = '127.0.0.1', port = 62743, nickname = None):
		self.host = host
		self.port = port 
		self.nickname = nickname

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
		self.server.connect((self.host, self.port))
		print(f"Connected to server")

		self.game = Game()
		self.started = False

		self.kill = False
		self.thread_count = 0


	# sends request r_type to server along with data
	def send(self, r_type, data):
		msg = {"type": r_type, "data": data}
		msg = json.dumps(msg).encode("utf-8")
		self.server.sendall(struct.pack("!I", len(msg)) + msg)		# pack length in first 4 bytes


	# receive server responses
	def receive(self):
		raw_len = self.server.recv(4)		# unpack length from first 4 bytes
		if not raw_len:
			return None

		(length,) = struct.unpack("!I", raw_len)

		msg = b""
		while len(msg) < length:
			more_msg = self.server.recv(length - len(msg))
			if not more:
				return None
			msg += more_msg

		return json.loads(msg.decode("utf-8"))


	# handle server responses
	def handle_receive(self, msg):
		r_type, data = msg.get("type"), msg.get("data")

		if r_type == Protocols.Response.GAME_STATE:
			self.game.deserialize(data)
		elif r_type == Protocols.Response.MOVE_VALID:		# highlight with green
			pass
		elif r_type == Protocols.Response.MOVE_INVALID:		# highlight with red
			pass
		elif r_type == Protocols.Response.NICKNAME:
			self.send(Protocols.Request.NICKNAME, self.nickname)
		elif r_type == Protocols.Response.START:
			self.started = True
			self.game.setup_game(data)
		elif r_type == Protocols.Response.RESULTS:
			self.game.update_results(data)
			self.kill = True
		# elif r_type == Protocols.Response.WAIT:		# means not started (covered under START)
		# 	pass


	# actively listening to server for responses (on thread)
	def server_listener(self):
		self.thread_count += 1

		self.server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
		self.server.settimeout(1)
		while not self.kill:
			try:
				msg = self.receive()
				self.handle_receive(msg)
			except socket.timeout:
				pass
			time.sleep(0.001)

		self.thread_count -= 1


	# awaiting all threads to kill themselves (only 1 thread here)
	def await_kill(self):
		self.kill = True
		while self.thread_count:
			time.sleep(0.01)
		print("Client killed")


	# main loop which updates game state
	def run(self):
		threading.Thread(target = self.server_listener).start()
		try:
			while not self.kill:
				self.kill = self.game.handle_events()		# to capture inputs (returns kill switch)
				move = self.game.draw(self.started)		# to render screen (returns move made by the player)
				if move:
					self.send(Protocols.Request.MOVE, move)
			self.game.handle_end()		# when game over
		except KeyboardInterrupt:
			
			pass
		self.await_kill()


if __name__ == "__main__":
	nickname = input("Enter nickname : ")
	while nickname == "":
		nickname = input("Enter VALID nickname : ")
	Client(host = "100.83.58.23", nickname = nickname).run()