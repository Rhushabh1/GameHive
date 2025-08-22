import socket
import threading
import json
import struct
import time

from protocols import Protocols
from room import Room


class Server:
	def __init__(self, host = '127.0.0.1', port = 62743, users = 2, bots = 0):
		self.host = host
		self.port = port 
		self.users = users
		self.bots = bots
		# total players = users + bots

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
		self.server.bind((self.host, self.port))
		print("Server created")

		self.clients = []
		self.client_names = []
		self.room = None
		self.waiting_for_players = False
		self.game_started = False

		self.kill = False
		self.thread_count = 0


	# sends {r_type, data} to client
	def send(self, r_type, data, client):
		msg = {"type": r_type, "data": data}
		msg = json.dumps(msg).encode("ascii")
		client.send(struct.pack("!I", len(msg)) + msg)		# pack length in first 4 bytes


	# setup the gaming env in room
	def create_room(self):
		self.room = Room(len(self.clients))
		print("Room created")
		self.room.initialise_board()
		self.waiting_for_players = False
		self.game_started = True


	# fetch nicknames and login details
	def handle_login(self, client):
		while not self.kill:
			self.send(Protocols.Response.NICKNAME, None, client)
			raw_len = client.recv(4)		# unpack length from first 4 bytes
			if raw_len:
				(length,) = struct.unpack("!I", raw_len)
				msg = client.recv(length)
				msg =json.loads(msg.decode("ascii"))			# capture client's nickname
				r_type, nickname = msg.get("type"), msg.get("data")
				time.sleep(0.001)

				if r_type == Protocols.Request.NICKNAME:
					self.client_names[self.clients.index(client)] = nickname
				else:
					continue

				if len(self.clients) < self.users:		# send clients to waiting lobby till all users have joined
					self.waiting_for_players = True
					print(f"Waiting Lobby = {len(self.clients)} Players")
					self.send(Protocols.Response.WAIT, None, client)		# inform client to wait
				else:
					self.create_room()		# create room since all users have joined
				
				break


	# let the clients sleep in the waiting lobby
	def waiting_lobby(self, client):
		while (not self.kill) and self.waiting_for_players:
			time.sleep(1)
		self.send(Protocols.Response.START, self.client_names, client)


	# handle client requests here
	def handle_receive(self, msg, client):
		r_type, data = msg.get("type"), msg.get("data")
		if r_type == Protocols.Request.MOVE:		# validate the move 
			valid = self.room.verify_move(self.clients.index(client), data)
			if not valid:
				self.send(Protocols.Response.MOVE_INVALID, None, client)
			else:
				self.send(Protocols.Response.MOVE_VALID, None, client)
		elif r_type == Protocols.Request.NEW_GAME:		# player sent to waiting when new game requested
			pass
		elif r_type == Protocols.Request.LEAVE:		# game ends when someone leaves the server
			pass


	# let the client disconnect gracefully (remove details from everywhere)
	def disconnect(self, client):
		client_id = self.clients.index(client)
		del self.clients[client_id]
		del self.client_names[client_id]
		client.close()


	# handles client connection (on thread)
	def handle_client(self, client):
		self.thread_count += 1

		client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
		client.settimeout(1)
		self.handle_login(client)
		self.waiting_lobby(client)
		while not self.kill:
			try:
				raw_len = client.recv(4)		# unpack length from first 4 bytes
				if raw_len:
					(length,) = struct.unpack("!I", raw_len)
					msg = client.recv(length)
					msg = json.loads(msg.decode("ascii"))
					self.handle_receive(msg, client)
			except socket.timeout:
				pass
			except (ConnectionAbortedError, ConnectionResetError):
				break
			time.sleep(0.001)
		
		self.disconnect(client)
		self.thread_count -= 1


	# listens for client connections (on thread)
	def connection_listener(self):
		self.thread_count += 1

		while (not self.kill) and (len(self.clients) < self.users):
			self.server.settimeout(1)
			self.server.listen()
			try:
				client, address = self.server.accept()
				print(f"Connected with {str(address)}")
				self.clients.append(client)
				self.client_names.append("")
				threading.Thread(target = self.handle_client, args = (client,)).start()
			except socket.timeout:
				continue
			time.sleep(0.01)

		self.thread_count -= 1


	# awaiting all threads to kill themselves
	def await_kill(self):
		self.kill = True 
		while self.thread_count:
			time.sleep(0.01)
		print("Server killed")		# all threads killed too


	# main loop, sends game state constantly to all clients
	def run(self):
		threading.Thread(target = self.connection_listener).start()		# spawns to listen for connections
		try:
			while True:
				if self.game_started:		# send game state to all only when game starts
					for i, client in enumerate(self.clients):
						try:
							self.send(Protocols.Response.GAME_STATE, self.room.serialize(i), client)
							if self.room.finished:
								self.send(Protocols.Response.RESULTS, self.room.leaderboard(), client)
						except OSError:		# if socket issue
							pass
					if self.room.finished:
						break
				time.sleep(0.05)
		except KeyboardInterrupt:		# Ctrl + C to shutdown server
			pass
		self.await_kill()				


if __name__ == "__main__":
	Server().run()