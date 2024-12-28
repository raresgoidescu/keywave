#!/usr/bin/env python3
import socket

PORT = 15243
def main():
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(("0.0.0.0", PORT))

	print(f'[INFO] Socket connected!')

	while (True):
		msg = input()

		print(f'[INFO] Will send "{msg}" to socket')
		client.send(msg.encode('utf-8'))

		res = client.recv(1024).decode('utf-8')
		print(f'Server responed with "{res}"')

if __name__ == '__main__':
	main()