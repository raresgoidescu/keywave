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

def store():
	pass

'''
server logic:
handle_user_login() {
	// check login details

	socket = get_socket(user)

	while (mq.has_msg(user)) {
		msg = mq.pop(user);
		send msg to user via socket
	}
}
'''

def has_msg(user):
	pass

def pop(user):
	pass