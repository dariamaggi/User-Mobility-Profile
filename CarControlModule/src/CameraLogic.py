import os
import time
import pathlib
# import picamera
import socket
# from picamera import PiCamera

from CommandLayer import request_remote_ump


# CATTURA FOTO E SALVATAGGIO IN PNG  E INVIO SU SOCKET DEL PNG


def get_foto():
    camera = PiCamera()
    counter = 0
    while 1 == 1:
        counter = counter + 1
        camera.start_preview()
        time.sleep(10)
        camera.capture(os.path.join(pathlib.Path(__file__), 'image.png'))
        camera.stop_preview()
        data = open(os.path.join(pathlib.Path(__file__), 'image.png'))
        user_id = request_user(counter, 'song', data)


def request_user(request_id, data_type, data):
    # costruisco al socket dal sensore all'auto
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((VEHICLE_URL, VEHICLE_IN_PORT))
    except Exception:
        traceback.print_exc()
        return

    logging.info("Sensor : socket to the vehicle successfully created")
    payload = {'requestID': request_id, 'dataType': data_type, 'data': data}

    # invio i dati
    s.sendall(json.dumps(payload).encode('utf-8'))

    logging.info("Sensor : request for userID sended")

    buffer = recv(s)
    s.close()
    logging.info("Sensor : Response received, socket closed")

    try:
        request_id = buffer["requestID"]
        user_id = buffer["userID"]
    except Exception:
        logging.info("Sensor  : failed in parsing the data")
        return False

    if request_id != request_id:
        logging.info("Sensor  : The request identificator doasn't correspond")
        return False

    return user_id


def recv(sock):
    res = ""
    buffer = bytearray()
    b = sock.recv(MTU)
    while len(b) > 0:
        buffer = buffer + b
        try:
            res = json.loads(buffer.decode('utf-8'))
            break
        except Exception:
            b = sock.recv(MTU)
    return res
