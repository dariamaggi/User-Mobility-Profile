import socket
import logging
import threading
import time
import traceback
import json

from UserMobilityProfileMain import recognize_user, modify_fields_user, recognize_user_server

MTU = 1024

# prendere dati da config file
config = configparser.ConfigParser()
path = Path(__file__).parent.parent
# config.read('/files/configurations.ini')
config.read(os.path.join(path, 'files', 'configurations.ini'))
setting = config['settings']
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

VEHICLE_IN_PORT =   65432 
VEHICLE_URL = '192.168.1.211'


def server_vehicle_accept(server_socket):
    while True:
        logging.info("Vehicle - T_accept : thread waiting connections" ) 
        clientsocket = "" 
        address = ""
        try: 
            (clientsocket, address) = serversocket.accept()
        except (Exception):
            traceback.print_exc() 
            logging.info("Vehicle - T_accept : failing in accepting the connection")
            continue

        logging.info("Vehicle - T_accept : new connection accepted from host -" + str(address) + "-")

        # creazione di un thread per gestire la ricezione dei dati dal sensore
        recv_thread = threading.Thread(target=server_vehicle_recv, args=(client_socket,))
        recv_thread.start()
        logging.info("Vehicle - T_accept : created new thread for the recv of the sensor data")

        # TODO ?????: creare una lista dei  client associati al cloud in questo momento
    return


def server_vehicle_recv(sensor_socket):
    logging.info("Vehicle - T_recv : wait for new buffer received from " + str(sensor_socket))

    buffer = recv(sensor_socket)

    logging.info("Vehicle - T_recv : new buffer received ")
    logging.info(str(buffer))

    # TODO: specificare l'eccezione sollevata
    try:
        request_id = buffer["requestID"]
        data_type = buffer["dataType"]
        data = buffer["data"]
    except Exception:
        logging.info("Vehicle - T_recv  : fail in parsing the data")
        return

    logging.info("Vehicle - T_recv : data successfully parsed")

    # bind con la parte di federico
    # user_id = identify_user(request_id, data_type, data)

    request_id = response[0]
    user_id = response[1]

    return_user_identifier(request_id, user_id, sensor_socket)

    sensor_socket.close()
    logging.info("Vehicle - T_recv : chiusura socket di comunicazione con il sensore " + str(sensor_socket))

    return


# # funzione chiamata dal sensore per ottenere un identificatore utente dal veicolo
# def request_user_identifier(request_id, data_type, data):
#     # costruisco al socket dal sensore all'auto
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     try:
#         s.connect((VEHICLE_URL, VEHICLE_IN_PORT))
#     except Exception:
#         traceback.print_exc()
#         return
#
#     logging.info("Sensor : socket to the vehicle successfully created")
#     payload = {'requestID': request_id, 'dataType': data_type, 'data': data}
#
#     # invio i dati
#     s.sendall(json.dumps(payload).encode('utf-8'))
#
#     logging.info("Sensor : request for userID sended")
#
#     buffer = recv(s)
#     s.close()
#     logging.info("Sensor : Response received, socket closed")
#
#     request_id = ""
#     user_id = ""
#     try:
#         request_id = buffer["requestID"]
#         user_id = buffer["userID"]
#     except Exception:
#         logging.info("Sensor  : failed in parsing the data")
#         return False
#
#     if request_id != request_id:
#         logging.info("Sensor  : The request identificator doasn't correspond")
#         return False
#
#     return user_id


    # invio i dati
    s.sendall( json.dumps( payload).encode('utf-8') )

    logging.info("Sensor : request for userID sended")
    
    buffer = recv( s )
    s.close()
    logging.info("Sensor : Response received, socket closed")
    
    request_id = ""
    user_id = ""
    try:
       request_id = buffer["requestID"]
       user_id = buffer["userID"]
    except(Exception):
        logging.info("Sensor  : failed in parsing the data")
        return False
    
    if request_id != requestID:
        logging.info("Sensor  : The request identificator doasn't correspond")
        return False

    return user_id

# f chiamata dal veicolo per rispondere alla richiesta del sensore
def return_user_identifier(request_id, user_id, sensor_socket):
    payload = {'requestID': request_id, 'userID': user_id}

    sensor_socket.sendall(json.dumps(payload).encode('utf-8'))
    logging.info("Vehicle - T_recv : invio buffer al sensore avvenuto con successo")
    logging.info(str(payload))
    return


vehicle_server = Server(VEHICLE_IN_PORT, "Vehicle - Main", server_vehicle_accept)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



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

        # TODO ????: creare una lista dei  client associati al cloud in questo momento
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
    # TODO: non ho capito
    # res = update_handler(buffer, vehicle_socket)
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

    inquiry_id = ""
    success_flag = ""

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
    # TODO: specificare l'eccezione sollevata

    try:
        inquiry_id = buffer["inquiryID"]
        data_type = buffer["dataType"]
        data = buffer["data"]
    except Exception:
        logging.info("Cloud - T_recv  : fail in parsing the data")
        return False

    logging.info("Cloud - T_recv : data successfully parsed")

    # bind con la parte di federico
    if data_type is 'modify':
        response = modify_fields_user(data['_id'], data['field'], data['value'])
        if response.acknowledged is not True:
            return False
        else:
            return True
    else:
        response = recognize_user_server(inquiry_id, data_type, data)
        inquiry_id = response[0]
        user_id = response[1]

    return return_remote_ump(inquiry_id, user_id, vehicle_socket)


def update_handler(buffer, vehicle_socket):
    inquiry_id = ""

    # TODO: specificare l'eccezione sollevata
    try:
        inquiry_id = buffer["inquiryID"]
        ump = buffer["UMP"]
    except Exception:
        logging.info("Cloud - T_recv  : fail in parsing the data")
        return

    logging.info("Cloud - T_recv : data successfully parsed")

    # bind con la parte di federico
    # res = update_ump( ump )
    res = True
    if res:
        res = "1"
    else:
        res = "0"

    payload = {'inquiryID': inquiry_id, 'success_flag': res}

    vehicle_socket.sendall(json.dumps(payload).encode('utf-8'))
    logging.info("Vehicle - T_recv : UMP successfully sended")
    return
