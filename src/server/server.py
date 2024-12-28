#!/usr/bin/env python3
import socket
import threading

PORT = 15243

def handle_client(socket: socket.socket, addr: tuple[str, int]):
	print(f'[INFO] New connection from address {addr}')

	# first message specifies (user, password)
	username = socket.recv(1024).decode('utf-8')
	print(f'[INFO] {addr} said: "{username}"')

	socket.send(f"I will remember that your name is {username}".encode('utf-8'))
	print(f'[INFO] Response sent :)')

	# db.verify() or db.new_user()
	# if verify() fails, respond with error and close socket

	# socket_map.store(username, socket)

	while True:
		message = socket.recv(1024).decode('utf-8')
		print(f'[INFO] {username} said "{message}"')

		# handle all types of events eventually
		response = f'Hi {username}, you said "{message}"'
		socket.send(response.encode('utf-8'))


def start():
	listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listener.bind(("0.0.0.0", PORT))
	listener.listen(128)
	print(f'[INFO] Listening on port {PORT}')

	while True:
		sck, addr = listener.accept()

		thread = threading.Thread(target=handle_client, args=(sck, addr))
		thread.start()


if __name__ == '__main__':
	start()