import socket
import logging
import configparser
from pathlib import Path
import os
import threading
import time
import traceback
import json

from UserMobilityProfileMain import modify_fields_user, recognize_user_server

# prendere dati da config file
config = configparser.ConfigParser()
path = Path(__file__).parent.parent
# config.read('/files/configurations.ini')
config.read(os.path.join(path, 'files', '../../files/configurations.ini'))
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


# ++++++++++++++++++++++++++++++++ Logica di comunicazione veicolo - cloud ++++++++++++++++++++++++++

CLOUD_IN_PORT = 55452
CLOUD_URL = '192.168.1.211'


def server_cloud_accept(server_socket):
    while True:
        logging.info("Cloud - T_accept : thread waiting connections")
        try:
            (client_socket, address) = server_socket.accept()
        except Exception:
            traceback.print_exc()
            logging.info("Cloud - T_accept : failing in accepting the connection")
            continue
        logging.info("Cloud - T_accept : new connection accepted from host -" + str(address) + "-")

        # creazione di un thread per gestire la ricezione dei dati dal veicolo
        recv_thread = threading.Thread(target=server_cloud_recv, args=(client_socket,))
        recv_thread.start()
        logging.info("Cloud - T_accept : created new thread for the recv of the sensor data")

    return


def server_cloud_recv(vehicle_socket):
    logging.info("Cloud - T_recv : wait for new buffer received from " + str(vehicle_socket))
    buffer = recv(vehicle_socket)

    logging.info("Cloud - T_recv : new buffer received ")
    logging.info(str(buffer))

    res = request_handler(buffer, vehicle_socket)

    if res:
        vehicle_socket.close()
        logging.info("Cloud - T_recv : closed socket with vehicle " + str(vehicle_socket))
        return
    res = update_handler(buffer, vehicle_socket)

    return res


cloud_server = Server(CLOUD_IN_PORT, "Cloud - Main", server_cloud_accept)


def return_remote_ump(inquiry_id, ump, vehicle_socket):
    payload = {'inquiryID': inquiry_id, 'UMP': ump}

    vehicle_socket.sendall(json.dumps(payload).encode('utf-8'))
    logging.info("Vehicle - T_recv : UMP successfully sended")
    return True


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


def update_remote_ump(inquiry_id, ump):
    s = socket.socket()
    s.connect((CLOUD_URL, CLOUD_IN_PORT))

    logging.info("Vehicle : socket to the cloud successfully created")
    payload = {'inquiryID': inquiry_id, 'UMP': ump}

    # invio i dati
    s.sendall(json.dumps(payload).encode('utf-8'))

    logging.info("Cloud : request for updating the UMP sended")

    buffer = recv(s)
    s.close()
    logging.info("Cloud : Response received, socket closed")

    try:
        inquiry_id = buffer["inquiryID"]
        success_flag = buffer["success_flag"]
    except Exception:
        logging.info("Cloud  : failed in parsing the data")
        return False

    if inquiry_id != inquiry_id:
        logging.info("Cloud  : invalid request id")
        return False

    if success_flag != "1":
        logging.info("Cloud  : fail to update the UMP on the cloud")
        return False

    return True


def request_handler(buffer, vehicle_socket):
    try:
        inquiry_id = buffer["inquiryID"]
        data_type = buffer["dataType"]
        data = buffer["data"]
    except Exception:
        logging.info("Cloud - T_recv  : fail in parsing the data")
        return False

    logging.info("Cloud - T_recv : data successfully parsed")

    response = recognize_user_server(inquiry_id, data_type, data)
    inquiry_id = response[0]
    user_id = response[1]

    return return_remote_ump(inquiry_id, user_id, vehicle_socket)


def update_handler(buffer, vehicle_socket):
    try:
        inquiry_id = buffer["inquiryID"]
        ump = buffer["UMP"]
    except Exception:
        logging.info("Cloud - T_recv  : fail in parsing the data")
        return False

    logging.info("Cloud - T_recv : data successfully parsed")

    # bind con la parte di federico
    response = modify_fields_user(ump['_id'], ump['field'], ump['value'])
    if response.acknowledged is True:
        res = '1'
    else:
        res = '0'

    payload = {'inquiryID': inquiry_id, 'success_flag': res}

    vehicle_socket.sendall(json.dumps(payload).encode('utf-8'))
    logging.info("Vehicle - T_recv : UMP successfully sended")
    return True
