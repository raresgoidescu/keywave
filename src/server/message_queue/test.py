#!/usr/bin/env python3
import string
import random

from src.server.message_queue.mq import *

def random_msg():
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def print_green(msg): print(f"\033[92m {msg}\033[00m")

def print_red(msg): print(f"\033[91m {msg}\033[00m")

def test_store_one():
	print('-' * 50)
	print('Running test-store-one ...\n')
	
	mq_init()
	test_username = random_msg()

	if not mq_has_msg(test_username):
		print_green('[PASS] is empty at the beginning')
	else:
		print_red('[FAIL] is empty at the beginning')

	msg1 = random_msg()
	mq_store(msg1, test_username)

	if mq_has_msg(test_username):
		print_green('[PASS] is not empty after storing one message')
	else:
		print_red('[FAIL] is not empty after storing one message')

	ret_msg1 = mq_pop_front(test_username)
	if ret_msg1 == msg1:
		print_green('[PASS] returned message is the same as before')
	else:
		print_red('[FAIL] returned message is the same as before')

	if not mq_has_msg(test_username):
		print_green('[PASS] is empty after consuming first message')
	else:
		print_red('[PASS] is empty after consuming first message')

	ret_msg2 = mq_pop_front(test_username)
	if ret_msg2 is None:
		print_green('[PASS] Pop returns None when no messages are available')
	else:
		print_red('[FAIL] Pop returns None when no messages are available')

	print('-' * 50)
	print('')


def test_store_multi():
	print('-' * 50)
	print('Running test-store-multi ...\n')
	
	mq_set_log_level(0)
	mq_init()
	test_username = random_msg()


	NUM_SAMPLES = 64
	messages = [random_msg() for _ in range(NUM_SAMPLES)]

	for msg in messages:
		mq_store(msg, test_username)

	test_fail = False
	i = 0
	while mq_has_msg(test_username):
		ret = mq_pop_front(test_username)

		if ret != messages[i]:
			test_fail = True
			print_red(f'fail on message #{i}, expected "{messages[i]}", got "{ret}"')
			break

		i += 1

	if test_fail:
		print_red('[FAIL] Returned messages are the same as queued messages')
	else:
		print_green('[PASS] Returned messages are the same as queued messages')

	if i == NUM_SAMPLES:
		print_green('[PASS] Loop consumed all elements')
	else:
		print_red('[FAIL] Loop consumed all elements')

	print('-' * 50)
	print('')

if __name__ == '__main__':
	test_store_one()
	test_store_multi()
