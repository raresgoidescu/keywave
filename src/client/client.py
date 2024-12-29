#!/usr/bin/env python3
import socket
import json

from src.data_structures.events import Events

def send_with_log(sck: socket.socket, msg: str):
	print(f'[INFO] Sending \'{msg}\' to server')
	sck.send(msg.encode('utf-8'))

	res = sck.recv(1024)
	print(f'[INFO] Received \'{res}\' from server')

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
		msg = input()

		print(f'[INFO] Will send "{msg}" to socket')
		client.send(msg.encode('utf-8'))

		res = client.recv(1024).decode('utf-8')
		print(f'Server responed with "{res}"')

if __name__ == '__main__':
	main()