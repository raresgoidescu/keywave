#!/usr/bin/env python3
import socket
import threading
import json
import time

from database.database import Database
from event_queue.event_queue import EventQueue
from socket_map.client_socket_map import ClientSocketMap

from src.data_structures.events import Events
from src.data_structures.generic_map import GenericMap

PORT = 18251

class Server():
	def __init__(self):
		self.users_db = Database()
		self.events = EventQueue()
		self.client_to_socket_map = ClientSocketMap()
		self.pending_requests = GenericMap()

	
	def handle_disconnect_event(self, parsed_event: dict, client: socket.socket, ctx: dict):
		print(f"[INFO] Client [uid = {ctx['uid']}] disconnected, shutting down socket")

		self.client_to_socket_map.remove_client(ctx['uid'])
		client.close()

		ctx['active'] = False


	def handle_chat_start_event(self, parsed_event: dict, client: socket.socket, ctx: dict):
		target_username = parsed_event['target']
		target_id = self.users_db.get_uid(target_username)
		print(f"[INFO] {target_username}'s id is {target_id}")

		if target_id < 0:
			client.send(f'{target_username} doesn\'t exist :('.encode('utf-8'))
			return

		target_sck = self.client_to_socket_map.get_client_socket(target_id)
		if target_sck is None:
			client.send(f'{target_username} is not online right now'.encode('utf-8'))
			return
		
		target_known = self.users_db.find_connection(ctx['uid'], target_id)
		event = {
			'type': Events.EVT_NEW_REQUEST.value,
			'source': ctx['username'],
			'known': target_known
		}
		self.events.store(event, target_id)

		self.pending_requests.add(ctx['uid'], target_id)
		
		#* 30 sec timeout, wait until target user accepts
		#* accepts => remove entry from the map
		#* rejects => sets entry to -1
		#* doesn't acknowledge => entry still there
		timestamp = time.time()
		print(timestamp)
		while (time.time() - timestamp) < 30:
			print(f'Delta = {time.time() - timestamp}, need 30 to timeout')

			time.sleep(.5)
			value = self.pending_requests.get(ctx['uid'])

			if value is None:
				# target accepted
				client.send('success'.encode('utf-8'))
				return
			
			if value == -1:
				client.send(f'{target_username} has refused the chat invite'.encode('utf-8'))
				return
		
		client.send(f'{target_username} didn\'t accept the invite in time'.encode('utf-8'))


	def handle_chat_invite_reject_event(self, parsed_event: dict, client: socket.socket, ctx: dict):
		target_username = parsed_event['target']
		target_id = self.users_db.get_uid(target_username)
		print(f"[INFO] {target_username}'s id is {target_id}")

		if target_id < 0:
			client.send(f'{target_username} doesn\'t exist :('.encode('utf-8'))
			return

		target_sck = self.client_to_socket_map.get_client_socket(target_id)
		if target_sck is None:
			client.send(f'{target_username} is not online right now'.encode('utf-8'))
			return
		
		target_pending_req = self.pending_requests.get(target_id)
		if target_pending_req == ctx['uid']:
			self.pending_requests.add(target_id, -1)
			client.send('success'.encode('utf-8'))
		else:
			client.send(f"Reject failed: {target_username}'s active invite is for a different user")

	
	def handle_chat_invite_accept_event(self, parsed_event: dict, client: socket.socket, ctx: dict):
		target_username = parsed_event['target']
		target_id = self.users_db.get_uid(target_username)
		print(f"[INFO] {target_username}'s id is {target_id}")

		if target_id < 0:
			client.send(f'{target_username} doesn\'t exist :('.encode('utf-8'))
			return

		target_sck = self.client_to_socket_map.get_client_socket(target_id)
		if target_sck is None:
			client.send(f'{target_username} is not online right now'.encode('utf-8'))
			return
		
		target_pending_req = self.pending_requests.get(target_id)
		if target_pending_req == ctx['uid']:
			self.pending_requests.remove(target_id)
			client.send('success'.encode('utf-8'))
		else:
			client.send(f"Reject failed: {target_username}'s active invite is for a different user")


	def handle_send_message_event(self, parsed_event: dict, client: socket.socket, ctx: dict):
		target_username = parsed_event['target']
		message_content = parsed_event['content']

		# todo early return if sender is not logged in 

		print(f"[INFO] {ctx['username']} (uid = {ctx['uid']}) wants to say '{message_content}' to {target_username}")

		target_id = self.users_db.get_uid(target_username)
		print(f"[INFO] {target_username}'s id is {target_id}")

		if target_id < 0:
			client.send(f'{target_username} doesn\'t exist :('.encode('utf-8'))
			return

		target_sck = self.client_to_socket_map.get_client_socket(target_id)

		event = {
			'type': Events.EVT_NEW_MESSAGE.value,
			'source': ctx['username'],
			'content': message_content
		}
		self.events.store(event, target_id)

		if target_sck is not None:
			print(f"[INFO] Will send '{message_content}' to {target_id}'s socket")
			client.send(f'Sent {message_content} to {target_username}'.encode('utf-8'))
		else:
			print(f"[INFO] {target_id} has no active socket, will store the message")
			client.send(f'{target_username} is not online, your message will be sent when they log in'.encode('utf-8'))


	def handle_acc_login_event(self, parsed_event: dict, client: socket.socket, ctx: dict):
		username = parsed_event['username']
		password = parsed_event['password']

		print(f"[INFO] Attempted login by '{username}' with pass '{password}'")
		acc_id = self.users_db.verify_user(username, password)
		print(f"[INFO] Retrieved id = {acc_id} for ['{username}', '{password}']")

		if acc_id > 0:
			ctx['username'] = username
			ctx['uid'] = acc_id

			self.client_to_socket_map.add_client(acc_id, client)

			friends = [i[0] for i in self.users_db.list_friends(acc_id)]
			res = json.dumps({
				'friends': friends,
				'status': 'success'
			})
			
			client.send(res.encode('utf-8'))
		else:
			res = json.dumps({
				'friends': [],
				'status': 'failure'
			})
			client.send(res.encode('utf-8'))

	def handle_acc_create_event(self, parsed_event: dict, client: socket.socket, ctx: dict):
		username = parsed_event['username']
		password = parsed_event['password']

		print(f"[INFO] Creating new account '{username}' with pass '{password}'")
		new_acc_id = self.users_db.add_user(username, password)

		if new_acc_id > 0:
			ctx['username'] = username
			ctx['uid'] = new_acc_id

			self.client_to_socket_map.add_client(new_acc_id, client)

			client.send('Login successful'.encode('utf-8'))
		else:
			client.send('Login failed'.encode('utf-8'))


	def handle_dh_event(self, parsed_event: str, client: socket.socket, ctx: dict, event: str):
		target_username = parsed_event['target']
		target_id = self.users_db.get_uid(target_username)
		print(f"[INFO] {target_username}'s id is {target_id}")

		if target_id < 0:
			client.send(f'{target_username} doesn\'t exist :('.encode('utf-8'))
			return

		target_sck = self.client_to_socket_map.get_client_socket(target_id)
		if target_sck is None:
			client.send(f'{target_username} is not online right now'.encode('utf-8'))
			return

		target_sck.send(event.encode('utf-8'))
		
		if parsed_event['event_type'] == Events.DH_ACK.value:
			print(f"[INFO] New connection stored between {ctx['uid']} and {target_id}")
			self.users_db.add_connection(ctx['uid'], target_id)


	def handle_client_refresh_event(self, event: str, client: socket.socket, ctx: dict):
		if ctx['username'] is None or ctx['uid'] == -1:
			client.send(f'[ERROR] you need to be logged in'.encode('utf-8'))
			return

		id = ctx['uid']
		updates = []
		while not self.events.empty(id):
			updates.append(self.events.pop_front(id))

		res = json.dumps({
			"updates": updates
		})
		client.send(res.encode('utf-8'))


	def handle_event(self, event: str, client: socket.socket, ctx: dict):
		parsed_event = {}		
		try:
			parsed_event = json.loads(event)
		except json.JSONDecodeError:
			client.send("Invalid event, not JSON".encode('utf-8'))
			return

		if "event_type" not in event:
			client.send("Invalid event, no type specified :(".encode('utf-8'))
			return

		event_type = int(parsed_event["event_type"])

		if event_type == Events.DISCONNECT.value:
			self.handle_disconnect_event(parsed_event, client, ctx)
		elif event_type == Events.REQ_ACC_LOGIN.value:
			self.handle_acc_login_event(parsed_event, client, ctx)
		elif event_type == Events.REQ_ACC_CREATE.value:
			self.handle_acc_create_event(parsed_event, client, ctx)
		elif event_type == Events.SEND_MESSAGE.value:
			self.handle_send_message_event(parsed_event, client, ctx)
		elif event_type == Events.REQ_SEND_UPDATES.value:
			self.handle_client_refresh_event(parsed_event, client, ctx)
		elif event_type == Events.REQ_START_CHAT.value:
			self.handle_chat_start_event(parsed_event, client, ctx)
		elif event_type == Events.REQ_CHAT_INV_ACCEPT.value:
			self.handle_chat_invite_accept_event(parsed_event, client, ctx)
		elif event_type == Events.REQ_CHAT_INV_REJECT.value:
			self.handle_chat_invite_reject_event(parsed_event, client, ctx)
		elif event_type == Events.DH_PUBLIC_SHARE.value or event_type == Events.DH_PUBLIC_ACK.value or event_type == Events.DH_KEY_SHARE.value or event_type == Events.DH_KEY_ACK_SHARE.value or event_type == Events.DH_ACK.value:
			self.handle_dh_event(parsed_event, client, ctx, event)
		else:
			client.send(f'Unknown event type {event_type}'.encode('utf-8'))


	def handle_client(self, socket: socket.socket, addr: tuple[str, int]):
		print(f'[INFO] New connection from address {addr}')

		context = {
			"username": None,
			"uid": -1,
			"active": True
		}

		while context['active']:
			message = socket.recv(1024).decode('utf-8')
			print(f'[INFO] {addr} (uid = {context["uid"]}) said: "{message}"')

			# handle all types of events eventually
			self.handle_event(message, socket, context)


	def start(self):
		listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listener.bind(("0.0.0.0", PORT))
		listener.listen(128)
		print(f'[INFO] Listening on port {PORT}')

		while True:
			sck, addr = listener.accept()

			thread = threading.Thread(target=self.handle_client, args=(sck, addr))
			thread.start()


if __name__ == '__main__':
	server = Server()
	server.start()