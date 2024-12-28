#!/usr/bin/env python3

from typing import override
import unittest
import socket
from unittest.mock import MagicMock
from src.socket_map.client_socket_map import ClientSocketMap

class TestClientSocketMap(unittest.TestCase):
    @override
    def setUp(self):
        self.client_map = ClientSocketMap()

        self.mock_socket1: socket.socket = MagicMock(spec=socket.socket)
        self.mock_socket2: socket.socket = MagicMock(spec=socket.socket)


    def test_add_and_get_client(self):
        self.client_map.add_client(1, self.mock_socket1)
        sock = self.client_map.get_client_socket(1)
        self.assertEqual(sock, self.mock_socket1)


    def test_remove_get_client(self):
        self.client_map.add_client(2, self.mock_socket2)
        res = self.client_map.remove_get_client(2)
        self.assertIsNone(self.client_map.get_client_socket(2))

        self.assertIsNotNone(res)

        if res != None:
            client, sock = res
            self.assertEqual(2, client)
            self.assertEqual(self.mock_socket2, sock)


    def test_remove_client(self):
        self.client_map.add_client(2, self.mock_socket2)
        self.client_map.remove_client(2)
        self.assertIsNone(self.client_map.get_client_socket(2))


    def test_get_non_existent_client(self):
        self.assertIsNone(self.client_map.get_client_socket(10))


    def test_list_clients(self):
        self.client_map.add_client(1, self.mock_socket1)
        self.client_map.add_client(2, self.mock_socket2)
        self.assertListEqual(self.client_map.get_clients(), [1, 2])

if __name__ == "__main__":
    _ = unittest.main()
