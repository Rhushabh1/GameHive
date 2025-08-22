class Protocols:
	class Response:		# sent by server
		NICKNAME = "protocols.request_nickname"
		WAIT = "protocols.wait"
		START = "protocols.start"
		GAME_STATE = "protocols.game_state"
		MOVE_VALID = "protocols.move_valid"
		MOVE_INVALID = "protocols.move_invalid"
		RESULTS = "protocols.results"

	class Request:		# sent by client
		NICKNAME = "protocols.send_nickname"
		MOVE = "protocols.move"
		NEW_GAME = "protocols.new_game"
		LEAVE = "protocols.leave"

