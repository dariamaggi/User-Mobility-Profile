from bson import ObjectId
from UserIdentificationLogicServer import *
import socket
import logging
import threading
import traceback
import json
from common.DatabaseConnector import *

# # prendere dati da config file
# config = configparser.ConfigParser()
# path = Path(__file__).parent.parent
# # config.read('/files/configurations.ini')
# config.read(os.path.join(path, 'files', '../../files/configurations.ini'))
# setting = config['settings']

MTU = 1024
CLOUD_IN_PORT = 55452
CLOUD_URL = '192.168.1.211'

# prendere dati da config file
config = configparser.ConfigParser()
path = Path(__file__).parent.parent.parent
config.read(os.path.join(path, 'files', 'configurations.ini'))
setting = config['settings']


def open_db():
    client = MongoClient(setting['mongo_con'])
    return client.UserProfileManagerDB


# Want ObjectId not the string of id
def get_user(user_id):
    db = open_db()
    return read_all_from_ump(ObjectId(user_id), db)


# Want ObjectId not the string of id
def get_field_of_user(user_id, field):
    db = open_db()
    return read_field_from_ump(ObjectId(user_id), db, field)


# Return Collection of users
def get_all_users():
    db = open_db()
    users = []
    collection = read_all_users(db)
    for user in collection:
        users.append(user)

    return users


# Want ObjectId not the string of id
def modify_fields_user(user_id, field, value):
    db = open_db()
    result = modify_to_ump(user_id, db, field, value)
    return result


# Write all images on files/photos and return True False
# The Images format are user_id + _ + counter(incremental) + .png
def get_all_image():
    db = open_db()
    return read_all_images(db)


# Write all sounds on files/sounds and return True False
# The Sounds format are user_id + _ + counter(incremental) + .mp3
def get_all_audio():
    db = open_db()
    return read_all_audios(db)


# Want ObjectId not the string of id
# Write all images on files/sounds and return True False
# The Images format are user_id + _ + counter(incremental) + .png
def get_images_by_id(user_id):
    db = open_db()
    counter = 0
    user_photos = read_images_by_id(db, user_id)
    if user_photos is None:
        return False
    for photo in user_photos:
        if photo is not None:
            output = open(os.path.join(setting['img_path'], str(user_id) + '_' + counter + '.png'), 'wb')
            output.write(photo)
            output.close()
            counter = counter + 1

    return True


# Want ObjectId not the string of id
# Write one image on files/sounds and return True False
# The Images format are user_id + .png
def get_image_by_id(user_id):
    db = open_db()
    user_photo = read_one_image_of_user(db, user_id)
    output = open(os.path.join(setting['img_path'], str(user_id) + '.png'), 'wb')
    output.write(user_photo[0])
    output.close()

    return True


# Want ObjectId not the string of id
# Write all images on files/sounds and return True False
# The Images format are user_id + _ + counter(incremental) + .mp3
def get_audios_by_id(user_id):
    db = open_db()
    counter = 0
    user_audios = read_audios_by_id(db, user_id)
    if user_audios is None:
        return False
    for audio in user_audios:
        if audio is not None:
            output = open(os.path.join(setting['sound_path'], str(user_id) + '_' + counter + '.wav'), 'wb')
            output.write(audio)
            output.close()
            counter = counter + 1

    return True


# Want ObjectId not the string of id
# Write one audio on files/sounds and return True False
# The audio format is user_id + .mp3
def get_audio_by_id(user_id):
    db = open_db()
    user_audio = read_one_song_of_user(db, user_id)
    output = open(os.path.join(setting['sound_path'], str(user_id) + '.wav'), 'wb')
    output.write(user_audio)
    output.close()


# Return a temp user and insert a temp user on db
def create_temp_user():
    db = open_db()
    list_fields = ['default', 'default', 'default', 43, 'default', 'default', 'default', 'default', 32,
                   'default', 98, 'default', 'default', 'default']
    user = create_user_json(list_fields)
    return create_user(db, user)


# Want ObjectId not the string of id
# Return DeleteResult
def delete_user_by_id(user_id):
    db = open_db()
    return delete_user(user_id, db)


# request_id -> numero di richiesta(deve essere incrementale)
# data_type -> deve essere song o photo
# data -> foto o suono serializzato
def recognize_user(request_id, data_type, data):
    db = open_db()
    if data_type is 'song':
        data_path = os.path.join(setting['temp_path'], 'temp' + '.wav')
        flag = 1
    elif data_type is 'photo':
        data_path = os.path.join(setting['temp_path'], 'temp' + '.png')
        flag = 0
    else:
        return False
    output = open(data_path, 'wb')
    output.write(data)
    output.close()
    user = identify_user(data_path, flag, db)

    response = []
    if user is None:
        logging.info('User is not identified on local')
        # todo: ricorda di cambiare questa cosa sul server
        user = request_user_cloud(request_id, data_type, data)
        if user is None:
            logging.info('User is not identified on cloud, create temp user')
            user = create_temp_user()
        else:
            create_user(db, user)

    response.insert(request_id)
    response.insert(user)

    os.remove(data_path)  # pulisce
    return response


def recognize_user_server(request_id, data_type, data):
    db = open_db()
    if data_type is 'song':
        data_path = os.path.join(setting['temp_path'], 'temp' + '.wav')
        flag = 1
    elif data_type is 'photo':
        data_path = os.path.join(setting['temp_path'], 'temp' + '.png')
        flag = 0
    else:
        return False
    output = open(data_path, 'wb')
    output.write(data)
    output.close()
    user = identify_user(data_path, flag, db)

    response = []
    if user is None:
        logging.info('User is not identified on server')

    response.insert(request_id)
    response.insert(None)

    os.remove(data_path)  # pulisce
    return response


def request_user_cloud(request_id, data_type, data):
    return request_remote_ump(request_id, data_type, data)


# TODO: da definire con Marsha e Andrea
def insert_user(user):
    db = open_db()
    create_user(db, user)

    return True


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
