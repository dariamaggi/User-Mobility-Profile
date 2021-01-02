import os

import pyaudio
import wave
import socket  # Import socket module
import logging
import time
import pathlib
from scipy.io.wavfile import read
import traceback
import json
import threading

form_1 = pyaudio.paInt16  # 16-bit resolution
chans = 1  # 1 channel
samp_rate = 44100  # 44.1kHz sampling rate
chunk = 4096  # 2^12 samples per buffer
record_secs = 3  # secondi di registrazione
dev_index = 2  # QUI VA INDICE DEL DISPOSITIVO AUDIO ottenunuto dalla p.get_device_info_by_index(ii) nel 3 comando

VEHICLE_IN_PORT = 65432
VEHICLE_URL = '192.168.1.211'
MTU = 1024


def get_audio():
    audio = pyaudio.PyAudio()  # istanza pyaudio
    counter = 0
    while 1 == 1:
        counter = counter + 1
        time.sleep(10)
        # create pyaudio stream
        stream = audio.open(format=form_1, rate=samp_rate, channels=chans,
                            input_device_index=dev_index, input=True,
                            frames_per_buffer=chunk)

        logging.info('Recorging....')
        frames = []

        # loop through stream and append audio chunks to frame array
        for ii in range(0, int((samp_rate / chunk) * record_secs)):
            data = stream.read(chunk)
            frames.append(data)

        logging.info('finished recording')

        # stop the stream, close it, and terminate the pyaudio instantiation
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # save the audio frames as .wav file
        wavefile = wave.open(os.path.join(pathlib.Path(__file__), 'song.wav'), 'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()

        data = read(os.path.join(pathlib.Path(__file__), 'song.wav'))
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
