import base64
import json
import logging
import _thread
import os
import pathlib
import socket  # Import socket module
import threading
import time
import traceback
import wave
from ctypes import *
import pyaudio
from picamera import PiCamera
from scipy.io.wavfile import read

form_1 = pyaudio.paInt16
chans = 1
samp_rate = 44100
chunk = 4096
record_secs = 5  # record time
dev_index = 2
wav_output_filename = 'audio.wav'

VEHICLE_IN_PORT = 65430
VEHICLE_URL = '127.0.1.1'
MTU = 1024

# $ grep -rn snd_lib_error_handler_t
# Define our error handler type
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)


def py_error_handler(filename, line, function, err, fmt):
    print('')


c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

asound = cdll.LoadLibrary('libasound.so')
# Set error handler
asound.snd_lib_error_set_handler(c_error_handler)


def get_photo():
    camera = PiCamera()
    print('Start camera')
    counter = 0
    while True:
        camera.resolution = (720, 576)
        counter = counter + 1
        camera.start_preview()
        name_photo = time.time()
        print('Capture photo')
        camera.capture(os.path.join('/home/pi/Desktop/project/files/photo/temp_sensor', str(name_photo) + '_image.png'))
        camera.stop_preview()
        data = open(os.path.join('/home/pi/Desktop/project/files/photo/temp_sensor', str(name_photo) + '_image.png'),
                    'rb')
        data_byte = data.read()
        start_time = time.time()
        print('Start connection')
        user_id = request_user(counter, 'photo', base64.encodebytes(data_byte).decode('utf-8'))
        print("--- %s seconds ---" % (time.time() - start_time))
        time.sleep(30)
        os.remove(os.path.join('/home/pi/Desktop/project/files/photo/temp_sensor', str(name_photo) + '_image.png'))


def get_audio():  # istanza pyaudio
    counter = 0
    print('start audio')
    while True:
        audio = pyaudio.PyAudio()
        counter = counter + 1
        # setup audio input stream
        stream = audio.open(format=form_1, rate=samp_rate, channels=chans, input_device_index=dev_index, input=True,
                            frames_per_buffer=chunk)
        print("recording\n")
        frames = []

        for ii in range(0, int((samp_rate / chunk) * record_secs)):
            data = stream.read(chunk, exception_on_overflow=False)
            frames.append(data)

        print("finished recording")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        # creates wave file with audio read in
        # Code is from the wave file audio tutorial as referenced below
        name_audio = time.time()
        wavefile = wave.open(
            os.path.join('/home/pi/Desktop/project/files/sounds/temp_sensor',
                         str(name_audio) + '_' + wav_output_filename),
            'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()

        data = open(
            os.path.join('/home/pi/Desktop/project/files/sounds/temp_sensor',
                         str(name_audio) + '_' + wav_output_filename),
            'rb')
        data_byte = data.read()
        start_time = time.time()
        user_id = request_user(counter, 'song', base64.encodebytes(data_byte).decode('utf-8'))
        print("--- %s seconds ---" % (time.time() - start_time))
        time.sleep(5)
        os.remove(
            os.path.join('/home/pi/Desktop/project/files/sounds/temp_sensor',
                         str(name_audio) + '_' + wav_output_filename))
        asound.snd_lib_error_set_handler(None)


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


def clean_folder():
    for f in os.listdir('/home/pi/Desktop/project/files/photo/temp_sensor'):
        os.remove(os.path.join('/home/pi/Desktop/project/files/photo/temp_sensor', f))

    for f in os.listdir('/home/pi/Desktop/project/files/sounds/temp_sensor'):
        os.remove(os.path.join('/home/pi/Desktop/project/files/sounds/temp_sensor', f))

    print('Clean all folder')


def main():
    """Entry point for the application script"""

    clean_folder()

    _thread.start_new_thread(get_audio, ())

    _thread.start_new_thread(get_photo, ())

    print("thread starts")


if __name__ == '__main__':
    print('Start sensors')
    main()
