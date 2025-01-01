#!/usr/bin/env python3
import socket
import json
import sys

from src.data_structures.events import Events

class Client():
	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.log_level = 0
		self.logged_in = False

		self.friends = []
		self.logs = {}

	
	def set_log_level(self, log_level: int):
		self.log_level = log_level


	def connect(self, addr: tuple[str, int]):
		self.socket.connect(addr)

		if self.log_level >= 2:
			print(f'[INFO] Socket connected')


	def __send_to_server(self, message: dict, no_receive=False):
		json_message = None
		try:
			json_message = json.dumps(message)
		except:
			if self.log_level >= 1:
				print(f'[ERROR] Cannot encode message :(')
			return
		
		self.socket.send(json_message.encode('utf-8'))
		if self.log_level >= 2:
			print(f'[INFO] Sending \'{json_message}\' to server')

		if no_receive:
			return None

		res = self.socket.recv(1024).decode('utf-8')
		if self.log_level >= 2:
			print(f'[INFO] Received \'{res}\' from server')

		return res


	def set_credentials(self, username: str, password: str):
		self.username = username
		self.password = password

	
	def send_acc_login(self):
		msg = {
			'event_type': Events.REQ_ACC_LOGIN.value,
			'username': self.username,
			'password': self.password
		}

		ret = self.__send_to_server(msg)
		self.logged_in = (ret == "Login successful")

		# todo grab friends from the server's db
		self.friends = [self.username]

		return ret


	def send_acc_create(self):
		msg = {
			'event_type': Events.REQ_ACC_CREATE.value,
			'username': self.username,
			'password': self.password
		}

		ret = self.__send_to_server(msg)
		self.logged_in = (ret == "Login successful")

		return ret

	
	def send_acc_delete(self):
		if self.log_level >= 1:
			print(f'[ERROR] This feature is not implemented yet')

		pass

	
	def send_message(self, target: str, content: str):
		msg = {
			'event_type': Events.SEND_MESSAGE.value,
			'source': self.username,
			'target': target,
			'content': content
		}

		return self.__send_to_server(msg)
	

	def get_updates(self):
		msg = {
			'event_type': Events.REQ_SEND_UPDATES.value
		}

		res = self.__send_to_server(msg)
		print(res)


	def start_chat(self, target: str):
		msg = {
			'event_type': Events.REQ_START_CHAT.value,
			'target': target
		}

		res = self.__send_to_server(msg)
		success = res == 'success'

		if success and self.log_level >= 2:
			print(f'[INFO] Chat start successful')
		elif not success and self.log_level >= 1:
			print(f'[INFO] Chat start failed, server reponse "{res}"')

		return success


	def log_new_message(self, target: str, content: str, own_message = False):
		sender = self.username if own_message else target

		if not target in self.logs:
			self.logs[target] = []

		self.logs[target].append(f'{sender}: {content}')


	def disconnect(self):
		msg = {
			'event_type': Events.DISCONNECT.value
		}

		_ = self.__send_to_server(msg, no_receive=True)

		self.logged_in = False
		self.socket.close()

		return None

PORT = 18251
def main():
	client = Client()
	client.connect(("0.0.0.0", PORT))

	username = input('Type username: ')
	password = input('Type password: ')

	client.set_credentials(username, password)

	login_res = client.send_acc_login()
	if not client.logged_in:
		choice = input('Login failed, would you like to create a new account with these credentials? [y/n]: ')

		if choice.lower() == 'y':
			client.send_acc_create()

	while (True):
		try:
			msg = input("Type your message: ")
			target = input("Recipient: ")

			_ = client.send_message(target, msg)

		except KeyboardInterrupt:
			print(f'[INFO] Disconnecting')
			client.disconnect()

			sys.exit(0)


if __name__ == '__main__':
	main()