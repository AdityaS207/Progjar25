from socket import *
import socket
import threading
import logging
from datetime import datetime

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = address

    def run(self):
        try:
            while True:
                data = self.connection.recv(1024)
                if not data:
                    break

                decoded_data = data.decode('utf-8').strip()
                logging.warning(f"Received from {self.address}: {repr(decoded_data)}")

                if decoded_data == "TIME":
                    now = datetime.now()
                    jam = now.strftime("%H:%M:%S")
                    response = f"JAM {jam}\r\n"
                    self.connection.sendall(response.encode('utf-8'))
                elif decoded_data == "QUIT":
                    logging.warning(f"Client {self.address} requested to quit.")
                    break
                else:
                    self.connection.sendall(b"UNKNOWN COMMAND\r\n")
        except Exception as e:
            logging.error(f"Exception from {self.address}: {e}")
        finally:
            self.connection.close()
            logging.warning(f"Connection with {self.address} closed.")

class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.the_clients = []

    def run(self):
        self.my_socket.bind(('0.0.0.0', 45000))
        self.my_socket.listen(5)
        logging.warning("Server listening on port 45000...")

        try:
            while True:
                connection, client_address = self.my_socket.accept()
                logging.warning(f"Connection from {client_address}")
                clt = ProcessTheClient(connection, client_address)
                clt.start()
                self.the_clients.append(clt)
        except KeyboardInterrupt:
            logging.warning("Server shutting down.")
        finally:
            self.my_socket.close()

def main():
    svr = Server()
    svr.start()

if __name__ == "__main__":
    main()
