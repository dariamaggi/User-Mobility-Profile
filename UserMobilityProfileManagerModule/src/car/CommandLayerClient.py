import socket
import logging
import configparser
from pathlib import Path
import os
import threading
import traceback
import json


from UserMobilityProfileMainClient import recognize_user

# prendere dati da config file
config = configparser.ConfigParser()
path = Path(__file__).parent.parent.parent
# config.read('/files/configurations.ini')
config.read(os.path.join(path, 'files', 'configurations.ini'))
setting = config['settings']

MTU = 1024


class Server:
    def __init__(self, port, type, accept_function):
        logging.basicConfig(level=logging.INFO)
        self.port = port
        self.type = type
        self.accept_function = accept_function

    def setup(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), self.port))
        self.socket.listen(5)

        logging.info(str(self.type) + "  : server socket created")
        logging.info(self.socket)

        self.server = threading.Thread(target=self.accept_function, args=(self.socket,))
        self.server.start()
        logging.info(str(self.type) + "  : server accept thread started")
        return


def recv(socket):
    res = ""
    buffer = bytearray()
    b = socket.recv(MTU)
    while len(b) > 0:
        buffer = buffer + b
        try:
            res = json.loads(buffer.decode('utf-8'))
            break
        except Exception:
            b = socket.recv(MTU)
    return res


# +++++++++++++++++++++       logica di comunicazione sensore - veicolo +++++++++++++++++++++++++++

VEHICLE_IN_PORT = 65432
VEHICLE_URL = '192.168.1.211'


def server_vehicle_accept(server_socket):
    while True:
        logging.info("Vehicle - T_accept : thread waiting connections")
        try:
            (client_socket, address) = server_socket.accept()
        except (Exception):
            traceback.print_exc()
            logging.info("Vehicle - T_accept : failing in accepting the connection")
            continue

        logging.info("Vehicle - T_accept : new connection accepted from host -" + str(address) + "-")

        # creazione di un thread per gestire la ricezione dei dati dal sensore
        recv_thread = threading.Thread(target=server_vehicle_recv, args=(client_socket,))
        recv_thread.start()
        logging.info("Vehicle - T_accept : created new thread for the recv of the sensor data")

    return


def server_vehicle_recv(sensor_socket):
    logging.info("Vehicle - T_recv : wait for new buffer received from " + str(sensor_socket))

    buffer = recv(sensor_socket)

    logging.info("Vehicle - T_recv : new buffer received ")
    logging.info(str(buffer))

    try:
        request_id = buffer["requestID"]
        data_type = buffer["dataType"]
        data = buffer["data"]
    except Exception:
        logging.info("Vehicle - T_recv  : fail in parsing the data")
        return

    logging.info("Vehicle - T_recv : data successfully parsed")

    response = recognize_user(request_id, data_type, data)
    request_id = response[0]
    user_id = response[1]

    return_user_identifier(request_id, user_id, sensor_socket)

    sensor_socket.close()
    logging.info("Vehicle - T_recv : chiusura socket di comunicazione con il sensore " + str(sensor_socket))

    return


# f chiamata dal veicolo per rispondere alla richiesta del sensore
def return_user_identifier(request_id, user_id, sensor_socket):
    payload = {'requestID': request_id, 'userID': user_id}

    sensor_socket.sendall(json.dumps(payload).encode('utf-8'))
    logging.info("Vehicle - T_recv : invio buffer al sensore avvenuto con successo")
    logging.info(str(payload))
    return


vehicle_server = Server(VEHICLE_IN_PORT, "Vehicle - Main", server_vehicle_accept)

# # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#
# # ++++++++++++++++++++++++++++++++ Logica di comunicazione veicolo - cloud ++++++++++++++++++++++++++
#
CLOUD_IN_PORT = 55452
CLOUD_URL = '192.168.1.211'

def request_remote_ump(inquiry_id, data_type, data):
    s = socket.socket()
    s.connect((CLOUD_URL, CLOUD_IN_PORT))

    logging.info("Vehicle : socket to the cloud successfully created")
    payload = {'inquiryID': inquiry_id, 'dataType': data_type, 'data': data}

    # invio i dati
    s.sendall(json.dumps(payload).encode('utf-8'))

    logging.info("Cloud : request for UMP sended")

    buffer = recv(s)
    s.close()
    logging.info("Cloud : Response received, socket closed")

    try:
        inquiry_id = buffer["inquiryID"]
        ump = buffer["UMP"]
    except(Exception):
        logging.info("Cloud  : failed in parsing the data")
        return False

    if inquiry_id != inquiry_id:
        logging.info("Cloud  : The request identificator doesn't correspond")
        return None

    return ump