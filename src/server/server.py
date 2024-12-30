#!/usr/bin/env python3
import socket
import threading
import json

from database.database import Database
from event_queue.event_queue import EventQueue
from socket_map.client_socket_map import ClientSocketMap

from src.data_structures.events import Events

PORT = 18251

class Server():
	def __init__(self):
		self.users_db = Database()
		self.events = EventQueue()
		self.client_to_socket_map = ClientSocketMap()

	
	def handle_disconnect_event(self, parsed_event: dict, client: socket.socket, ctx: dict):
		print(f"[INFO] Client [uid = {ctx['uid']}] disconnected, shutting down socket")

		self.client_to_socket_map.remove_client(ctx['uid'])
		client.close()

		ctx['active'] = False

	
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
			'type': Events.EVT_NEW_MESSAGE,
			'content': {
				'source': ctx['username'],
				'content': message_content
			}
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

			client.send('Login successful'.encode('utf-8'))
		else:
			client.send('Login failed'.encode('utf-8'))

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


	def handle_friend_request_event(self, parsed_event: str, client: socket.socket, ctx: dict):
		if 'username' not in ctx:
			client.send(f'[ERROR] you need to be logged in')
			return
		
		if 'target' not in ctx:
			client.send(f'[ERROR] no target')
			return
		
		source = ctx['username']
		target = ctx['target']

		# todo check if they're already friends

		target_id = self.users_db.get_uid(target)
		if target_id < 0:
			client.send(f'[ERROR] User \'{target}\' doesn\'t exist')
			return
		
		target_sck = self.client_to_socket_map.get_client_socket()
		if target_sck is None:
			client.send(f"[ERROR] User '{target}' is not online")
			return
		
		# todo check if user is talking to someone else

		# todo queue this request and send to the target client


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