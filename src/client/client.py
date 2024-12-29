#!/usr/bin/env python3
import socket
import json
import sys

from src.data_structures.events import Events

def send_with_log(sck: socket.socket, msg: str, no_receive=False):
	print(f'[INFO] Sending \'{msg}\' to server')
	sck.send(msg.encode('utf-8'))

	if no_receive:
		return ""
	
	res = sck.recv(1024)
	print(f'[INFO] Received \'{res}\' from server')

	return res


def send_disconnect(sck: socket.socket):
	msg = json.dumps({
		'event_type': Events.DISCONNECT.value
	})

	res = send_with_log(sck, msg, no_receive=True)
	return res


def send_login(sck: socket.socket, username: str, password: str):
	msg = json.dumps({
		'event_type': Events.REQ_ACC_LOGIN.value,
		'username': username,
		'password': password
	})

	res = send_with_log(sck, msg)

	return res.decode('utf-8')


def send_create_account(sck: socket.socket, username: str, password: str):
	msg = json.dumps({
		'event_type': Events.REQ_ACC_CREATE.value,
		'username': username,
		'password': password
	})

	res = send_with_log(sck, msg)

	return res.decode('utf-8')

def send_message(sck: socket.socket, username: str, target: str, content: str):
	msg = json.dumps({
		'event_type': Events.SEND_MESSAGE.value,
		'source': username,
		'target': target,
		'content': content
	})

	res = send_with_log(sck, msg)
	return res.decode('utf-8')

PORT = 18251
def main():
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(("0.0.0.0", PORT))

	print(f'[INFO] Socket connected!')

	username = input('Type username: ')
	password = input('Type password: ')

	login_res = send_login(client, username, password)
	if login_res == "Login failed":
		choice = input('Login failed, would you like to create a new account with these credentials? [y/n]: ')
		if choice == 'y':
			send_create_account(client, username, password)

	while (True):
		try:
			msg = input("Type your message: ")
			target = input("Recipient: ")

			_ = send_message(client, username, target, msg)

		except KeyboardInterrupt:
			print(f'[INFO] Disconnecting')
			send_disconnect(client)

			client.close()
			sys.exit(0)


if __name__ == '__main__':
	main()