from enum import Enum

class Events(Enum):
	DISCONNECT = 0
	REQ_ACC_LOGIN = 1
	REQ_ACC_CREATE = 2
	REQ_ADD_FRIEND = 3
	REQ_SEND_UPDATES = 4
	REQ_START_CHAT = 5
	# todo DH events
	SEND_MESSAGE = 10

	# client events
	EVT_NEW_MESSAGE = 201
	EVT_NEW_REQUEST = 202

