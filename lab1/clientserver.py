"""
Client and server using classes
"""

import logging
import socket

import const_cs
from context import lab_logging


d = lab_logging.setup(stream_level=logging.INFO)

class Server:
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)
        self._logger.info(f"Server bound to socket {self.sock}")
        
        self.phonebook = {
            "Alice": "1234",
            "Bob": "5678",
            "Charlie": "9012"
        }

    def serve(self):
        self.sock.listen(1)
        self._logger.info("Server listening for connections...")
        while self._serving:
            try:
                conn, addr = self.sock.accept()
                self._logger.info(f"Accepted connection from {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break

                    request = data.decode('utf-8').strip()
                    self._logger.info(f"Received request: '{request}'")

                    if request == "GETALL":
                        response = str(self.phonebook)
                    elif request.startswith("GET "):
                        _, name = request.split(maxsplit=1)
                        response = self.phonebook.get(name, "NOT FOUND")
                    else:
                        response = "INVALID REQUEST"

                    self._logger.info(f"Sending response: '{response}'")
                    conn.send(response.encode('utf-8'))

                conn.close()
                self._logger.info(f"Connection with {addr} closed")
            except socket.timeout:
                pass

        self.sock.close()
        self._logger.info("Server shutdown.")


class Client:
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((const_cs.HOST, const_cs.PORT))
        self._logger.info(f"Client connected to socket {self.sock}")

    def call(self, command="GET Alice"):
        self._logger.info(f"Sending command: '{command}'")
        self.sock.send(command.encode('utf-8'))
        data = self.sock.recv(4096)
        response = data.decode('utf-8')
        self._logger.info(f"Received response: '{response}'")
        print(response)
        return response
    
    def get(self, name):
        return self.call("GET " + name)
    
    def getall(self):
        return self.call("GETALL")

    def close(self):
        self.sock.close()
        self._logger.info("Client socket closed.")