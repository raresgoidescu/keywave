from enum import Enum

class Events(Enum):
	DISCONNECT = 0
	REQ_ACC_LOGIN = 1
	REQ_ACC_CREATE = 2
	REQ_ADD_FRIEND = 3
	# todo DH events
	SEND_MESSAGE = 10

