from queue import Queue

# 0 = nothing, 1 = errors only, 2 = normal
MQ_LOG_LEVEL = 2
user_to_queue_map = {}

def mq_init():
	user_to_queue_map.clear()

	if MQ_LOG_LEVEL >= 2:
		print(f'[INFO] Initialised message storage with an empty map')

	return True

def mq_set_log_level(level):
	global MQ_LOG_LEVEL
	
	if level < 0:
		level = 0
	
	if level > 2:
		level = 2

	MQ_LOG_LEVEL = level

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


def mq_store(msg, target: str):
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

def mq_has_msg(username: str):
	q = __get_queue(username)

	return q.qsize() > 0


def mq_pop_front(username: str):
	q = __get_queue(username)

	if q.qsize() == 0:
		if MQ_LOG_LEVEL >= 1:
			print(f'[WARN] Trying to get message for user \'{username}\' with empty queue')

		return None

	return q.get(block=False)