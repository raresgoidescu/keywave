#!/usr/bin/env python3
import socket
import json

from src.data_structures.events import Events

def send_with_log(sck: socket.socket, msg: str):
	print(f'[INFO] Sending \'{msg}\' to server')
	sck.send(msg.encode('utf-8'))

	res = sck.recv(1024)
	print(f'[INFO] Received \'{res}\' from server')

PORT = 18251
def main():
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(("0.0.0.0", PORT))

	print(f'[INFO] Socket connected!')

	username = input('Type username: ')
	password = input('Type password: ')

	first_message = json.dumps({
		'event_type': Events.REQ_ACC_LOGIN.value,
		'username': username,
		'password': password
	})

	res = send_with_log(client, first_message)

	while (True):
		msg = input()

		print(f'[INFO] Will send "{msg}" to socket')
		client.send(msg.encode('utf-8'))

		res = client.recv(1024).decode('utf-8')
		print(f'Server responed with "{res}"')

if __name__ == '__main__':
	main()