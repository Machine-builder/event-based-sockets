from os import stat
import socket
import pickle
import select
import errno
from typing import Union, List, Tuple
import logging


class utility:
    ...


class constants:
    ...


class ebsocket_base:
    ...


class ebsocket_event:
    ...


class utility():
    @staticmethod
    def try_unpickle(obj: bytes):
        '''tests if obj is a pickled object.
        If it is, return the unpickled object,
        otherwise, return None'''
        try:
            return pickle.loads(obj)
        except:
            return None

    @staticmethod
    def pickle_object(obj: any) -> bytes:
        '''dumps provided object using pickle.dumps()'''
        return pickle.dumps(obj)

    @staticmethod
    def any_type_join(l: list, j: str) -> str:
        '''concatenates a list of any object type with j as the connecting string'''
        return j.join([str(a) for a in l])

    @staticmethod
    def get_header(data: bytes, headersize: int = 16):
        '''generates a header for byte data'''
        return str(len(data)).rjust(headersize, '0').encode()

    @staticmethod
    def get_local_ip() -> str:
        '''gets local ipv4 address'''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ipv4 = s.getsockname()[0]
        s.close()
        return ipv4


class constants:
    header_size = 16


class ebsocket_base(object):
    '''base class for both the server & client ebsocket classes'''

    def __init__(self, connection: socket.socket) -> None:
        self.connection = connection

    def is_valid_socket(self, socket_) -> socket.socket:
        '''if socket_ is a socket.socket instance the function returns it,
        otherwise returns the class instances' connection attribute'''
        if not isinstance(socket_, socket.socket):
            return self.connection
        return socket_

    def send_raw_to(self, data: bytes, connection: socket.socket):
        '''sends raw byte data to specific connection'''
        connection.send(data)

    def send_raw(self, data: bytes):
        '''sends raw byte data'''
        self.send_raw_to(data, self.connection)

    def recv_raw_from(self, buffersize: int = 34, connection: socket.socket = ...):
        '''receives a ray payload of the provided buffer size from a specific connection'''
        return connection.recv(buffersize)

    def recv_raw(self, buffersize: int = 512):
        '''receives a raw payload of the provided buffer size'''
        return self.recv_raw_from(buffersize, self.connection)

    def send_with_header(self, data: bytes, send_socket: socket.socket = None):
        '''sends data with a header'''
        use_socket = self.is_valid_socket(send_socket)
        byte_data = utility.get_header(data, constants.header_size)+data
        use_socket.send(byte_data)

    def recv_with_header(self, recv_socket: socket.socket = None):
        '''receives data with a header'''
        use_socket = self.is_valid_socket(recv_socket)
        header_recv = use_socket.recv(constants.header_size)
        try:
            total_bytes = int(header_recv.decode())
            data_recv = use_socket.recv(total_bytes)
            return data_recv
        except:
            return None

    def send_event(self, event: ebsocket_event = None, send_socket: socket.socket = None):
        '''sends an event using send_socket'''
        use_socket = self.is_valid_socket(send_socket)
        raw_bytes = utility.pickle_object(event)
        return self.send_with_header(raw_bytes, use_socket)

    def recv_event(self, recv_socket: socket.socket = None):
        '''attempts to receive and return an event object, if the object
        received is not an event object, the function returns None'''
        use_socket = self.is_valid_socket(recv_socket)
        raw_bytes = self.recv_with_header(use_socket)
        if raw_bytes is None:
            return None
        loaded_event: ebsocket_event = utility.try_unpickle(raw_bytes)
        if isinstance(loaded_event, ebsocket_event):
            return loaded_event
        return None


class ebsocket_server(ebsocket_base):
    '''a server class used to handle multiple socket connections'''

    def __init__(self, bind_to: Union[tuple, int]):
        if isinstance(bind_to, int):
            bind_to = (utility.get_local_ip(), bind_to)
        self.address = bind_to
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.bind(self.address)

    def listen(self, backlog: int = 1):
        '''listens for incoming connections with a backlog'''
        self.connection.listen(backlog)

    def accept_connection(self) -> tuple:
        '''accepts next incoming connection and returns the connection and address'''
        connection, address = self.connection.accept()
        return connection, address


class ebsocket_client(ebsocket_base):
    '''a client class used to handle a single connection'''

    def __init__(self) -> None:
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        super().__init__(self.connection)

    def connect_to(self, address: tuple):
        '''try connect to an address, the connected attribute is
        a boolean which will be set to True if the connection is a success'''
        try:
            self.connection.connect(address)
            self.connected = True
            self.connection.setblocking(False)
        except:
            self.connected = False

    def pump(self):
        '''gets a list of all new events from the server

        also returns a boolean representing whether the connection
        is still active'''
        new_events = []

        try:
            while True:
                new_event = self.recv_event()
                if new_event is None:
                    return new_events, False
                new_events.append(new_event)

        except ConnectionResetError as e:
            return new_events, False

        except IOError as e:
            if e.errno != errno.EAGAIN and errno != errno.EWOULDBLOCK:
                # reading error
                logging.info(f"reading error in get_new_events() -> {e}")

        except Exception as e:
            # general error
            logging.info(f"general error in get_new_events() -> {e}")

        return new_events, True


class ebsocket_system(object):
    '''a whole server-client system network'''

    def __init__(self, server: ebsocket_server) -> None:
        self.server = server
        self.server.listen(5)
        self.connections_list = [self.server.connection]
        self.clients = {}

    def pump(self) -> Tuple[List[Tuple], List[ebsocket_event], List[Tuple]]:
        '''runs the main system

        run this function within a loop for basic functionality

        returns:
         - new_clients:list
         - new_events:list
         - disconnected_clients:list'''

        read_connections, _, exception_connections = select.select(
            self.connections_list, [], self.connections_list)

        new_clients = []
        new_events = []
        disconnected_clients = []

        for notified_connection in read_connections:
            if notified_connection == self.server.connection:
                client_connection, client_address = self.server.accept_connection()
                self.connections_list.append(client_connection)
                self.clients[client_connection] = client_address
                new_clients.append((client_connection, client_address))

            else:
                try:
                    event = self.server.recv_event(notified_connection)
                except ConnectionResetError as e:
                    event = None
                    exception_connections.append(notified_connection)

                if event is not None:
                    event.from_connection = notified_connection
                    new_events.append(event)

        for notified_connection in exception_connections:
            disconnected_clients.append(
                (notified_connection, self.clients[notified_connection]))
            self.remove_client(notified_connection)

        return new_clients, new_events, disconnected_clients

    def remove_client(self, client_connection):
        '''removes a client from the server'''
        self.connections_list.remove(client_connection)
        del self.clients[client_connection]

    def send_raw_to(self, connection: socket.socket, data: bytes):
        '''sends byte data to a client'''
        connection.send(data)

    def send_event_to(self, connection: socket.socket, event: ebsocket_event):
        '''sends an event to a client'''
        data = utility.pickle_object(event)
        header = utility.get_header(data)
        self.send_raw_to(connection, header+data)

    def send_event_to_clients(self, event: ebsocket_event):
        '''sends an event to all clients'''
        data = utility.pickle_object(event)
        header = utility.get_header(data)
        raw_bytes = header+data
        for client_connection in self.clients:
            self.send_raw_to(client_connection, raw_bytes)


class ebsocket_event(object):
    '''an event
    stores the event type and event data'''

    def __init__(self, event_data, **kwargs) -> None:
        self.from_connection = False
        if isinstance(event_data, str):
            self.__dict__ = {'event': event_data}
            self.__dict__.update(kwargs)
        elif isinstance(event_data, ebsocket_event):
            self.__dict__ = event_data.data
            self.from_connection = event_data.from_connection
        else:
            self.__dict__ = event_data
        self.event = self.__dict__.get('event', None)

    def get_attribute(self, attribute):
        '''gets an attribute of the event's data, if the attribute
        does not exist, returns None'''
        return self.__dict__.get(attribute, None)

    def compare_type(self, event_type:str) -> bool:
        '''compare the event's type with the provided argument'''
        return self.event == event_type

    def __repr__(self):
        return f'ebsocket_event<{self.event}>'
    
    def print_attributes(self):
        '''prints all event data attributes'''
        attribute_names = [k for k in self.attributes]
        print(self)
        print('~ attributes ~')
        if len(attribute_names) > 0:
            longest = max([len(i) for i in attribute_names])
            for attribute_name in attribute_names:
                print(f' * {attribute_name.ljust(longest)}  :  {self.attributes[attribute_name]}')
        else:
            print("event has no attributes")
