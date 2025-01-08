#!/usr/bin/env python3
import base64
import random
import socket
import json
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend

from src.data_structures.events import Events

class Client():
	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.log_level = 0
		self.logged_in = False

		self.friends = []
		self.logs = {}
		self.pending_invites = []

		self.key = 0


	def set_log_level(self, log_level: int):
		self.log_level = log_level


	def connect(self, addr: tuple[str, int]):
		self.socket.connect(addr)

		if self.log_level >= 2:
			print(f'[INFO] Socket connected')


	def __listen(self):
		if self.log_level >= 2:
			print(f'Waiting on server to send a message ...')

		res = self.socket.recv(1024).decode('utf-8')

		if self.log_level >= 2:
			print(f'[INFO] Received \'{res}\' from server')

		return res


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

		return self.__listen()


	def set_credentials(self, username: str, password: str):
		self.username = username
		self.password = password


	def set_key(self, key: int):
		self.key = key


	def send_acc_login(self):
		msg = {
			'event_type': Events.REQ_ACC_LOGIN.value,
			'username': self.username,
			'password': self.password
		}

		res = self.__send_to_server(msg)
		res_json = json.loads(res)
		self.logged_in = (res_json['status'] == "success")

		self.friends = res_json['friends']

		return res


	def add_connection(self, friend: str):
		if friend not in self.friends:
			self.friends.append(friend)


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
		cipher_bytes, iv_bytes, salt_bytes = self.__encrypt_content(content, self.key)

		b64_content_bytes = base64.b64encode(cipher_bytes)
		b64_content_string = b64_content_bytes.decode("utf-8")

		b64_iv_bytes = base64.b64encode(iv_bytes)
		b64_iv_string = b64_iv_bytes.decode("utf-8")

		b64_salt_bytes = base64.b64encode(salt_bytes)
		b64_salt_string = b64_salt_bytes.decode("utf-8")

		b64_content = {
			'b64_content': b64_content_string,
			'b64_iv': b64_iv_string,
			'b64_salt': b64_salt_string
		}

		msg = {
			'event_type': Events.SEND_MESSAGE.value,
			'source': self.username,
			'target': target,
			'content': b64_content
		}

		return self.__send_to_server(msg)


	def __encrypt_content(self, content: str, key: int):
		if self.log_level >= 2:
			print(f'[INFO] Encrypting content with key {key} ...')

		key_bytes = key.to_bytes(key.bit_length() // 8 + 1, 'big')

		if self.log_level >= 2:
			print(f'[INFO] Key bytes: {key_bytes} of len {len(key_bytes)}')

		salt = random.randbytes(16)

		if self.log_level >= 2:
			print(f'[INFO] Salt: {salt} of len {len(salt)}')

		hkdf = HKDF(
			algorithm=SHA256(),
			salt=salt,
			info=b'key-derivation',
			length=32,
			backend=default_backend()
		)

		derived_key = hkdf.derive(key_bytes)

		if self.log_level >= 2:
			print(f'[INFO] Derived key: {derived_key} of len {len(derived_key)}')

		iv = random.randbytes(16)

		if self.log_level >= 2:
			print(f'[INFO] IV: {iv} of len {len(iv)}')

		cipher = Cipher(
			algorithms.AES(derived_key),
			modes.CBC(iv),
			backend=default_backend()
		)

		encryptor = cipher.encryptor()
		padder = padding.PKCS7(algorithms.AES.block_size).padder()

		padded_content = padder.update(content.encode('utf-8')) + padder.finalize()

		if self.log_level >= 2:
			print(f'[INFO] Padded content: {padded_content} of len {len(padded_content)}')

		ciphertext = encryptor.update(padded_content) + encryptor.finalize()

		if self.log_level >= 2:
			print(f'[INFO] Ciphertext: {ciphertext} of len {len(ciphertext)} and type {type(ciphertext)}')

		return ciphertext, iv, salt


	def __decrypt_content(self, content: str, key: int, iv: bytes, salt: bytes):
		key_bytes = key.to_bytes(key.bit_length() // 8 + 1, 'big')

		hkdf = HKDF(
			algorithm=SHA256(),
			salt=salt,
			info=b'key-derivation',
			length=32,
			backend=default_backend()
		)

		derived_key = hkdf.derive(key_bytes)

		cipher = Cipher(
			algorithms.AES(derived_key),
			modes.CBC(iv),
			backend=default_backend()
		)

		decryptor = cipher.decryptor()
		unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

		decrypted_content = decryptor.update(content) + decryptor.finalize()

		message = unpadder.update(decrypted_content) + unpadder.finalize()

		return message.decode('utf-8')


	def get_updates(self):
		msg = {
			'event_type': Events.REQ_SEND_UPDATES.value
		}

		res = self.__send_to_server(msg)

		if self.log_level >= 2:
			print(f"[INFO] Received updates from the server: '{res}'")

		try:
			res_decoded = json.loads(res)
		except:
			return

		if 'updates' not in res_decoded:
			return

		updates = res_decoded['updates']
		for update in updates:
			if update['type'] == Events.EVT_NEW_REQUEST.value:
				self.pending_invites.append({
					'source': update['source'],
					'known': update['known']
				})
			elif update['type'] == Events.EVT_NEW_MESSAGE.value:
				iv_bytes = base64.b64decode(update['content']['b64_iv'])
				salt_bytes = base64.b64decode(update['content']['b64_salt'])
				content_bytes = base64.b64decode(update['content']['b64_content'])

				content = self.__decrypt_content(content_bytes, self.key, iv_bytes, salt_bytes)

				self.log_new_message(update['source'], content)


	def begin_key_exchange(self, target: str, role:int):
		if role == 1:
			return self.__key_exchange_A(target)
		elif role == 2:
			return self.__key_exchange_B(target)
		else:
			return None


	def __key_exchange_A(self, target: str):
		p = 23 # todo generate this value, not hardcode
		g = 5 # todo generate this value, not hardcode

		msg1 = {
			'event_type': Events.DH_PUBLIC_SHARE.value,
			'source': self.username,
			'target': target,
			'mod': p,
			'base': g
		}

		res2 = self.__send_to_server(msg1)
		res2_json = json.loads(res2)
		if (self.log_level >= 2):
			print(f'[INFO] Received response from server: {res2_json}')

		if res2_json['event_type'] != Events.DH_PUBLIC_ACK.value or res2_json['source'] != target or res2_json['target'] != self.username:
			# todo send cancel to server
			return None

		if res2_json['mod'] != p or res2_json['base'] != g:
			# todo send cancel to server
			return None

		secret_a = random.randint(500, 600)
		A = (g ** secret_a) % p

		msg3 = {
			'event_type': Events.DH_KEY_SHARE.value,
			'source': self.username,
			'target': target,
			'key': A
		}

		res4 = self.__send_to_server(msg3)
		res4_json = json.loads(res4)
		if (self.log_level >= 2):
			print(f'[INFO] Received response from server: {res4_json}')

		if res4_json['ack'] != A:
			# todo send cancel
			return None

		B = res4_json['key']
		secret = (B ** secret_a) % p

		msg5 = {
			'event_type': Events.DH_ACK.value, 
			'source': self.username,
			'target': target,
			'ack': B
		}

		self.__send_to_server(msg5, no_receive=True)
		return secret


	def __key_exchange_B(self, target: str):
		res1 = self.__listen()
		res1_json = json.loads(res1)
		if (self.log_level >= 2):
			print(f'[INFO] Received response from server: {res1_json}')

		if res1_json['event_type'] != Events.DH_PUBLIC_SHARE.value or res1_json['source'] != target or res1_json['target'] != self.username:
			# todo send cancel to server
			return None

		mod = res1_json['mod']
		base = res1_json['base']

		msg2 = {
			'event_type': Events.DH_PUBLIC_ACK.value, 
			'source': self.username,
			'target': target,
			'mod': mod,
			'base': base
		}

		res3 = self.__send_to_server(msg2)
		res3_json = json.loads(res3)
		if (self.log_level >= 2):
			print(f'[INFO] Received response from server: {res3_json}')

		A = res3_json['key']

		secret_b = random.randint(700, 800)
		B = (base ** secret_b) % mod

		msg4 = {
			'event_type': Events.DH_KEY_ACK_SHARE.value,
			'source': self.username,
			'target': target,
			'ack': A,
			'key': B,
		}

		secret = (A ** secret_b) % mod

		res5 = self.__send_to_server(msg4)
		res5_json = json.loads(res5)
		if res5_json['event_type'] != Events.DH_ACK.value or res5_json['ack'] != B:
			# todo send cancel
			return None

		return secret;


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


	def reject_invite(self):
		if len(self.pending_invites) == 0:
			if self.log_level >= 1: 
				print(f"[ERROR] reject_invite() got called, but no invites are pending")

			return

		target = self.pending_invites.pop()
		msg = {
			'event_type': Events.REQ_CHAT_INV_REJECT.value,
			'target': target['source']
		}
		return self.__send_to_server(msg)


	def accept_invite(self):
		if len(self.pending_invites) == 0:
			if self.log_level >= 1: 
				print(f"[ERROR] accept_invite() got called, but no invites are pending")

			return

		target = self.pending_invites.pop()
		msg = {
			'event_type': Events.REQ_CHAT_INV_ACCEPT.value,
			'target': target['source']
		}
		return self.__send_to_server(msg)


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