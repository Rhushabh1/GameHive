# GameHive
A hive of multiplayer online games

GameHive is a platform hosting multiple online multiplayer games built in Python. It provides a client-server architecture where players can join games, play in real-time, and interact with bots if the player count is low

## Features
- Multiplayer online gameplay
- Client-Server architecture
- Bot support for incomplete games
- Simple lobby interface with player matchmaking
- Easy-to-extend framework for adding new games

## Installation & Setup
1. Clone the repository:

$> git clone https://github.com/Rhushabh1/GameHive.git
$> cd GameHive

2. Run the setup script to install required Python packages:

$> bash setup.sh

3. Start the server for your chosen game:

$> python server.py

4. Launch the client to play the game:

$> python client.py

## How to Play
1. Launch the client and enter your nickname
2. Wait in the lobby until other players join
3. Start the game when ready
4. Play the game until it ends
5. Results are displayed at the end
6. Choose to start a NEW GAME or QUIT

## Project Structure

GameHive/

setup.sh 		# installs dependencies
README.md 		# project documentation

<GAME>/
	server.py 		#
	client.py 		#
	room.py 		#
	game.py 		#
	bot.py 			#
	protocols.py 	#
	assets/ 		#