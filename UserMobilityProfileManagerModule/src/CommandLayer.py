import socket
import logging
import threading
import time

MTU = 1024

class Server:
    def __init__(self, port, type, accept_function):
        self.port = port
        self.type = type
        self.accept_function = accept_function   

    def setup(self):
        self.socket = socket.socket()
        self.socket.bind((socket.gethostname(), self.port))
        self.socket.listen(5)
        
        logging.info( type + "  : server socket created")
        
        self.server = threading.Thread(target=self.accept_function, args=(self.socket, ))
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
        
        # TODO ?????: creare una lista dei  client associati al cloud in questo momento
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
    logging.info("Vehicle - T_recv : chiusura socket di comunicazione con il sensore " + sensorsocket.gethostname())
    
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

    sensorsocket.send( payload )
    logging.info("Vehicle - T_recv : invio user_id al sensore avvenuto con successo")
    return

vehicle_server = Server(VEHICLE_IN_PORT, "Vehicle - Main", server_vehicle_accept)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



# ++++++++++++++++++++++++++++++++ Logica di comunicazione veicolo - cloud ++++++++++++++++++++++++++

CLOUD_IN_PORT = 22222222
CLOUD_URL = 'localhost'

def server_cloud_accept( serversocket ):
    while True: 
        (clientsocket, address) = serversocket.accept()
        logging.info("Cloud - T_accept : new connection accepted from host -" + address + "-" )
        
        # creazione di un thread per gestire la ricezione dei dati dal veicolo
        recv_thread = threading.Thread(target=server_cloud_recv, args=(clientsocket, ))
        logging.info("Cloud - T_accept : created new thread for the recv of the sensor data" )
        
        # TODO ????: creare una lista dei  client associati al cloud in questo momento
    return

def server_vehicle_recv( vehicleSocket ):    
    buffer = recv( vehicleSocket )

    logging.info("Cloud - T_recv : new buffer received from " + vehicleSocket.gethostname() )

    res = requestHandler( buffer, vehicleSocket )

    if res:
        vehicleSocket.close()
        logging.info("Cloud - T_recv : closed socket with vehicle " + vehicleSocket.getHostName() )
        return

    res = updateHandler( buffer, vehicleSocket )
    return

cloud_server = Server(CLOUD_IN_PORT, "Cloud - Main", server_cloud_accept)

def returnRemoteUMP( inquiryID, UMP, vehicleSocket ):    
    payload = {}

    payload['inquiryID'] = inquiryID
    payload['UMP'] = UMP

    vehicleSocket.send( payload )
    logging.info("Vehicle - T_recv : UMP successfully sended")
    return

def requestRemoteUMP(inquiryID, dataType, data): 
    s = socket.socket()
    s.connect( (CLOUD_URL, CLOUD_IN_PORT) )

    logging.info("Vehicle : socket to the cloud successfully created")
    payload = {}

    payload['inquiryID'] = inquiryID
    payload['dataType'] = dataType
    payload['data'] = data

    # invio i dati
    s.send( payload )

    logging.info("Cloud : request for UMP sended")

    buffer = recv( s )
    s.close()
    logging.info("Cloud : Response received, socket closed")

    inquiry_id = ""
    ump = ""

    try:
        inquiry_id = buffer["inquiryID"]
        ump = buffer["UMP"]
    except(Exception):
        logging.info("Cloud  : failed in parsing the data")
        return False

    if inquiry_id != inquiryID:
        logging.info("Cloud  : The request identificator doasn't correspond")
        return False

    return ump

def updateRemoteUMP(inquiryID, UMP):
    s = socket.socket()
    s.connect( (CLOUD_URL, CLOUD_IN_PORT) )

    logging.info("Vehicle : socket to the cloud successfully created")
    payload = {}
    payload['inquiryID'] = inquiryID
    payload['UMP'] = UMP

    # invio i dati
    s.send( payload )

    logging.info("Cloud : request for updating the UMP sended")

    buffer = recv( s )
    s.close()
    logging.info("Cloud : Response received, socket closed")

    inquiry_id = ""
    success_flag = ""

    try:
        inquiry_id = buffer["inquiryID"]
        success_flag = buffer["success_flag"]
    except(Exception):
        logging.info("Cloud  : failed in parsing the data")
        return False

    if inquiry_id != inquiryID:
        logging.info("Cloud  : invalid request id")
        return False

    if success_flag != "1":
        logging.info("Cloud  : fail to update the UMP on the cloud")
        return False
            
    return True

def requestHandler(buffer, vehicleSocket):
    inquiry_id = ""
    data_type = ""
    data = ""

    # TODO: specificare l'eccezione sollevata
    try:
       inquiry_id = buffer["inquiryID"]
       data_type = buffer["dataType"]
       data = buffer["data"]
    except(Exception):
        logging.info("Cloud - T_recv  : fail in parsing the data")
        return False
        
    logging.info("Cloud - T_recv : data successfully parsed")

    # bind con la parte di federico
    # user_id = identify_user(request_id, data_type, data)

    user_id = "123456789"

    returnRemoteUMP(inquiry_id, user_id, vehicleSocket)

    return True

def updateHandler(buffer, vehicleSocket):
    inquiry_id = ""
    ump = ""
    
    # TODO: specificare l'eccezione sollevata
    try:
       inquiry_id = buffer["inquiryID"]
       ump = buffer["UMP"]
    except(Exception):
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

    payload = {}

    payload['inquiryID'] = inquiry_id
    payload['success_flag'] = res

    vehicleSocket.send( payload )
    logging.info("Vehicle - T_recv : UMP successfully sended")
    return





        
