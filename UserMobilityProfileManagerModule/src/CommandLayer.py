import socket
import logging
import threading
import time
import traceback
import json

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
        
        logging.info( str(self.type) + "  : server socket created")
        logging.info( self.socket )

        self.server = threading.Thread(target=self.accept_function, args=(self.socket, ))
        self.server.start()
        logging.info( str(self.type) + "  : server accept thread started")
        return

def recv( socket ):
    res = ""
    buffer = bytearray()    
    b = socket.recv(MTU)
    while( len(b) > 0 ):
        buffer = buffer + b
        try:
            res = json.loads( buffer.decode('utf-8') )
            break 
        except(Exception):
            b = socket.recv(MTU)
    return res
        
# +++++++++++++++++++++       logica di comunicazione sensore - veicolo +++++++++++++++++++++++++++

VEHICLE_IN_PORT =   65432 
VEHICLE_URL = '192.168.1.211'

def server_vehicle_accept( serversocket ):
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

        logging.info("Vehicle - T_accept : new connection accepted from host -" + str(address) + "-" )
        
        # creazione di un thread per gestire la ricezione dei dati dal sensore
        recv_thread = threading.Thread(target=server_vehicle_recv, args=(clientsocket, ))
        recv_thread.start()
        logging.info("Vehicle - T_accept : created new thread for the recv of the sensor data" )
        
        # TODO ?????: creare una lista dei  client associati al cloud in questo momento
    return

def server_vehicle_recv( sensorsocket ):
    logging.info("Vehicle - T_recv : wait for new buffer received from " + str( sensorsocket ) )

    buffer = recv( sensorsocket )

    logging.info("Vehicle - T_recv : new buffer received " )
    logging.info(str(buffer))

    request_id = ""
    data_type = ""
    data = ""

    # TODO: specificare l'eccezione sollevata
    try:
       request_id = buffer["requestID"]
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
    logging.info("Vehicle - T_recv : chiusura socket di comunicazione con il sensore " + str(sensorsocket) )
    
    return

# funzione chiamata dal sensore per ottenere un identificatore utente dal veicolo
def requestUserIdentifier(requestID, dataType, data):
    # costruisco al socket dal sensore all'auto
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect( (VEHICLE_URL, VEHICLE_IN_PORT) )
    except(Exception):
        traceback.print_exc()
        return

    logging.info("Sensor : socket to the vehicle successfully created")
    payload = {}

    payload['requestID'] = requestID
    payload['dataType'] = dataType
    payload['data'] = data

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
def returnUserIdentifier(requestID, userID, sensorsocket):
    
    payload = {}

    payload['requestID'] = requestID
    payload['userID'] = userID

    sensorsocket.sendall( json.dumps( payload).encode('utf-8') )
    logging.info("Vehicle - T_recv : invio buffer al sensore avvenuto con successo")
    logging.info(str(payload))
    return

vehicle_server = Server(VEHICLE_IN_PORT, "Vehicle - Main", server_vehicle_accept)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



# ++++++++++++++++++++++++++++++++ Logica di comunicazione veicolo - cloud ++++++++++++++++++++++++++

CLOUD_IN_PORT = 55452
CLOUD_URL = '192.168.1.211'

def server_cloud_accept( serversocket ):
    while True: 
        logging.info("Cloud - T_accept : thread waiting connections" ) 
        clientsocket = ""
        address = ""
        try: 
            (clientsocket, address) = serversocket.accept()
        except (Exception):
            traceback.print_exc() 
            logging.info("Cloud - T_accept : failing in accepting the connection")
            continue
        logging.info("Cloud - T_accept : new connection accepted from host -" + str(address) + "-" )
        
        # creazione di un thread per gestire la ricezione dei dati dal veicolo
        recv_thread = threading.Thread(target=server_cloud_recv, args=(clientsocket, ))
        recv_thread.start()
        logging.info("Cloud - T_accept : created new thread for the recv of the sensor data" )
        
        # TODO ????: creare una lista dei  client associati al cloud in questo momento
    return

def server_cloud_recv( vehicleSocket ): 
    logging.info("Cloud - T_recv : wait for new buffer received from " + str( vehicleSocket ) )   
    buffer = recv( vehicleSocket )

    logging.info("Cloud - T_recv : new buffer received " )
    logging.info(str(buffer) )

    res = requestHandler( buffer, vehicleSocket )

    if res:
        vehicleSocket.close()
        logging.info("Cloud - T_recv : closed socket with vehicle " + str( vehicleSocket)  )
        return

    res = updateHandler( buffer, vehicleSocket )
    return res

cloud_server = Server(CLOUD_IN_PORT, "Cloud - Main", server_cloud_accept)

def returnRemoteUMP( inquiryID, UMP, vehicleSocket ):    
    payload = {}

    payload['inquiryID'] = inquiryID
    payload['UMP'] = UMP

    vehicleSocket.sendall( json.dumps( payload).encode('utf-8') )
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
    s.sendall( json.dumps( payload).encode('utf-8') )

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
    s.sendall( json.dumps( payload).encode('utf-8') )

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

    vehicleSocket.sendall( json.dumps( payload).encode('utf-8') )
    logging.info("Vehicle - T_recv : UMP successfully sended")
    return





        
