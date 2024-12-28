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


	def handle_event(self, event: str, client: socket.socket):
		parsed_event = json.loads(event)

		if "event_type" not in event:
			client.send("Invalid event, no type specified :(")

		event_type = int(parsed_event["event_type"])

		if event_type == Events.REQ_ACC_LOGIN.value:
			username = parsed_event['username']
			password = parsed_event['password']

			print(f"[INFO] Attempted login by '{username}' with pass '{password}'")
			valid_login = self.users_db.verify_user(username, password)
			
			if valid_login:
				# todo save to some kind of context
				client.send('Login successful (allegedly)'.encode('utf-8'))
			else:
				client.send('Login failed'.encode('utf-8'))

		else:
			client.send(f'Unknown event type {event_type}'.encode('utf-8'))

	def handle_client(self, socket: socket.socket, addr: tuple[str, int]):
		print(f'[INFO] New connection from address {addr}')

		# first message specifies (user, password)
		first_message = socket.recv(1024).decode('utf-8')
		print(f'[INFO] {addr} said: "{first_message}"')

		self.handle_event(first_message, socket)

		# db.verify() or db.new_user()
		# if verify() fails, respond with error and close socket

		# socket_map.store(username, socket)

		# while True:
		# 	message = socket.recv(1024).decode('utf-8')
		# 	print(f'[INFO] {username} said "{message}"')

		# 	# handle all types of events eventually
		# 	response = f'Hi {username}, you said "{message}"'
		# 	socket.send(response.encode('utf-8'))


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