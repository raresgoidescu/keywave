from queue import Queue

# 0 = nothing, 1 = errors only, 2 = normal
MQ_LOG_LEVEL = 2
user_to_queue_map = None

def mq_init():
	user_to_queue_map = {}

	if MQ_LOG_LEVEL >= 2:
		print(f'[INFO] Initialised message storage with an empty map')

	return True

'''
server logic:

handle_message(msg, target) {
	socket = get_socket(target)
	if (socket != null) {
		// send msg to target via socket
	}
	else {
		mq.store(target, msg) // store message for later 
	}
}
'''

def __get_queue(target: str) -> Queue:
	if target not in user_to_queue_map:
		user_to_queue_map[target] = Queue()

	return user_to_queue_map[target]


def store(msg, target: str):
	q = __get_queue(target)

	q.put(msg)

	if MQ_LOG_LEVEL >= 2:
		print(f'[INFO] New message for user \'{target}\' stored in queue')
	

'''
server logic:
handle_user_login() {
	// check login details

	socket = get_socket(user)

	while (mq.has_msg(user)) {
		msg = mq.pop_front(user);

		// send msg to user via socket
	}
}
'''

def has_msg(username: str):
	q = __get_queue(username)

	return q.qsize() > 0


def pop_front(username: str):
	q = __get_queue(username)

	return q.get()