import socket

from src.data_structures.generic_map import GenericMap

class ClientSocketMap:
    def __init__(self):
        # Generic map to store client ID (int) to socket mapping
        self.client_map: GenericMap[int, socket.socket] = GenericMap()

        print(f"[INFO] Initialized Map(Client ID -> Socket)!")


    def add_client(self, client_id: int, client_socket: socket.socket):
        '''
        Add a client ID and its associated socket.

        :param client_id: Unique identifier for the client (e.g. ID from db)
        :param client_socket: The socket object associated with the client
        '''
        self.client_map.add(client_id, client_socket)

        print(f'Added an entry ("{client_id}", "{client_socket.__hash__}"')


    def remove_client(self, client_id: int):
        '''
        Remove a client and its associated socket based on the client ID.
        NOTE: Callee's responsability to close the socket connection.

        :param client_id: Unique identifier for the client (e.g. ID from db)
        '''
        sock = self.client_map.get(client_id)

        if sock != None:
            sock.close()

        self.client_map.remove(client_id)

        print(f'Removed an entry ("{client_id}")')


    def remove_get_client(self, client_id: int):
        '''
        Remove and retrieve a client and its associated socket based on the client ID.
        NOTE: Caller's responsability to close the socket connection.

        :param client_id: Unique identifier for the client (e.g. ID from db)
        :return: Tuple (client_id: int, client_socket: socket.socket)
        '''
        print(f'Removed an entry ("{client_id}")')

        return self.client_map.remove_and_get(client_id)


    def get_client_socket(self, client_id: int):
        '''
        Get the client's associated socket based on the client ID.

        :param client_id: Unique identifier for the client (e.g. ID from db)
        :return: the socket: socket.socket associated with the client ID
        '''
        return self.client_map.get(client_id)


    def get_clients(self):
        '''
        Get all the clients in the map.

        :return: list of clients
        '''
        return self.client_map.get_keys()
