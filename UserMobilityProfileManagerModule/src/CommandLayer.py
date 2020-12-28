import socket
import logging
import threading
import time

MTU = 1024

class Server:
    def __init__(self, port, type, accept_function):
        self.socket = socket.socket()
        
        self.socket.bind((socket.gethostname(), port))
        self.socket.listen(5)
        logging.info( type + "  : server socket created")

        self.server = threading.Thread(target=accept_function, args=(self.socket, ))
        self.server.start()
        logging.info( type + "  : server accept thread started")
        return

def recv( socket ):
    buffer = ""    
    b = socket.receive(MTU)
    while( len(b) > 0 ):
        buffer = buffer + b
        b = socket.receive(MTU)
    return buffer
        
# +++++++++++++++++++++       logica di comunicazione sensore - veicolo +++++++++++++++++++++++++++

VEHICLE_IN_PORT = 11111
VEHICLE_URL = 'localhost'

def server_vehicle_accept( serversocket ):
    while True: 
        (clientsocket, address) = serversocket.accept()
        logging.info("Vehicle - T_accept : new connection accepted from host -" + address + "-" )
        
        # creazione di un thread per gestire la ricezione dei dati dal sensore
        recv_thread = threading.Thread(target=server_vehicle_recv, args=(clientsocket, ))
        logging.info("Vehicle - T_accept : created new thread for the recv of the sensor data" )
        
        # TODO: creare una lista dei  client associati al cloud in questo momento
    return

def server_vehicle_recv( sensorsocket ):

    buffer = recv( sensorsocket )

    logging.info("Vehicle - T_recv : new buffer received from " + sensorsocket.gethostname() )

    request_id = ""
    data_type = ""
    data = ""

    # TODO: specificare l'eccezione sollevata
    try:
       request_id = buffer["requestId"]
       data_type = buffer["dataType"]
       data = buffer["data"]
    except(Exception):
        logging.info("Vehicle - T_recv  : fail in parsing the data")
        return
        
    logging.info("Vehicle - T_recv : data successfully parsed")

    # bind con la parte di federico
    # user_id = identify_user(request_id, data_type, data)

    user_id = "123456789"

    returnUserIdentifier(request_id, user_id, sensorsocket)

    sensorsocket.close()
    return

# funzione chiamata dal sensore per ottenere un identificatore utente dal veicolo
def requestUserIdentifier(requestID, dataType, data):
    # costruisco al socket dal sensore all'auto
    s = socket.socket()
    s.connect( (VEHICLE_URL, VEHICLE_IN_PORT) )

    logging.info("Sensor : socket to the vehicle successfully created")
    payload = {}

    payload['requestID'] = requestID
    payload['dataType'] = dataType
    payload['data'] = data

    # invio i dati
    s.send( payload )

    logging.info("Sensor : request for userID sended")
    
    buffer = recv( s )
    s.close()
    logging.info("Sensor : Response received, socket closed")
    
    request_id = ""
    user_id = ""
    try:
       request_id = buffer["requestId"]
       user_id = buffer["userID"]
    except(Exception):
        logging.info("Sensor  : failed in parsing the data")
        return False
    
    if request_id != requestID:
        logging.info("Sensor  : The request identificator doasn't correspond")
        return False

    return user_id

# f chiamata dal veicolo per rispondere alla richiesta del sensore
def returnUserIdentifier(requestID, userID, sensorsocket):
    
    payload = {}

    payload['requestID'] = requestID
    payload['userID'] = userID

    sensorsocket.send( sensorsocket )

    return

vehicle_server = Server(VEHICLE_IN_PORT, "Vehicle - Main", server_vehicle_accept)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def returnRemoteUMP( inquiryID, UMP, conn = cloud_conn ):    
    return

def requestRemoteUMP(self, inquiryID, UMP): 
    return

def updateRemoteUMP(self, inquiryID, UMP):
    return


def returnUserIdentifier(self, requestID, dataType, data):
    return

def requestUserIdentifier(self, requestID, dataType, data):
    return




        
