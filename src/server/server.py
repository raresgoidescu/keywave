#!/usr/bin/env python3
import socket
import threading
import json

from database.database import Database
from message_queue.mq import *
from socket_map.client_socket_map import ClientSocketMap

from src.data_structures.events import Events

PORT = 18251

class Server():
	def __init__(self):
		self.users_db = Database()

		mq_init()
		mq_set_log_level(0)

		self.client_to_socket_map = ClientSocketMap()

	
	def handle_disconnect_event(self, parsed_event: dict, client: socket.socket, ctx: dict):
		print(f"[INFO] Client disconnected, shutting down socket")
		client.close()

		ctx['active'] = False


	def handle_acc_login_event(self, parsed_event: dict, client: socket.socket, ctx: dict):
		username = parsed_event['username']
		password = parsed_event['password']

		print(f"[INFO] Attempted login by '{username}' with pass '{password}'")
		valid_login = self.users_db.verify_user(username, password)
		
		if valid_login:
			ctx['username'] = username
			client.send('Login successful'.encode('utf-8'))
		else:
			client.send('Login failed'.encode('utf-8'))

	def handle_acc_create_event(self, parsed_event: dict, client: socket.socket, ctx: dict):
		username = parsed_event['username']
		password = parsed_event['password']

		print(f"[INFO] Creating new account '{username}' with pass '{password}'")
		acc_created = self.users_db.add_user(username, password)
		
		if acc_created:
			ctx['username'] = username
			client.send('Login successful'.encode('utf-8'))
		else:
			client.send('Login failed'.encode('utf-8'))


	def handle_event(self, event: str, client: socket.socket, ctx: dict):
		parsed_event = json.loads(event)

		if "event_type" not in event:
			client.send("Invalid event, no type specified :(".encode('utf-8'))

		event_type = int(parsed_event["event_type"])

		if event_type == Events.DISCONNECT.value:
			self.handle_disconnect_event(parsed_event, client, ctx)
		elif event_type == Events.REQ_ACC_LOGIN.value:
			self.handle_acc_login_event(parsed_event, client, ctx)
		elif event_type == Events.REQ_ACC_CREATE.value:
			self.handle_acc_create_event(parsed_event, client, ctx)
		else:
			client.send(f'Unknown event type {event_type}'.encode('utf-8'))


	def handle_client(self, socket: socket.socket, addr: tuple[str, int]):
		print(f'[INFO] New connection from address {addr}')

		context = {
			"username": None,
			"active": True
		}

		while context['active']:
			message = socket.recv(1024).decode('utf-8')
			print(f'[INFO] {addr} said: "{message}"')

			# handle all types of events eventually
			self.handle_event(message, socket, context)


	def start(self):
		# initialise database
		users_database = Database()

		# initialise message queue
		mq_init()
		mq_set_log_level(2)

		# initialise socket map
		client_to_socket_map = ClientSocketMap()

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