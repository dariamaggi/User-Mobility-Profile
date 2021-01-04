import os
import threading

import pyaudio
import wave
import socket  # Import socket module
import logging
import time
import pathlib
from scipy.io.wavfile import read
import traceback
import json
from picamera import PiCamera

form_1 = pyaudio.paInt16
chans = 1
samp_rate = 44100
chunk = 4096
record_secs = 5  # record time
dev_index = 2
wav_output_filename = 'audio.wav'

VEHICLE_IN_PORT = 65432
VEHICLE_URL = '192.168.1.211'
MTU = 1024


def get_photo():
    camera = PiCamera()
    print('Start camera')
    counter = 0
    while 1 == 1:
        counter = counter + 1
        # camera.start_preview()
        time.sleep(1)
        camera.capture(os.path.join(pathlib.Path(__file__), 'image.png'))
        # camera.stop_preview()
        data = open(os.path.join(pathlib.Path(__file__), 'image.png'))
        user_id = request_user(counter, 'photo', data)
        time.sleep(10)


def get_audio():  # istanza pyaudio
    counter = 0
    audio = pyaudio.PyAudio()
    print('start audio')
    while 1 == 1:
        counter = counter + 1

        # setup audio input stream
        stream = audio.open(format=form_1, rate=samp_rate, channels=chans, input_device_index=dev_index, input=True,
                            frames_per_buffer=chunk)
        print("recording")
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
        wavefile = wave.open(wav_output_filename, 'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()

        # plays the audio file
        os.system("aplay" + wav_output_filename)

        data = read(os.path.join(pathlib.Path(__file__), wav_output_filename))
        user_id = request_user(counter, 'song', data)

        time.sleep(10)


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


def main():
    """Entry point for the application script"""

    t1 = threading.Thread(target=get_audio())
    t1.start

    t2 = threading.Thread(target=get_photo())
    t2.start

    print("Call your main application code here")


if __name__ == '__main__':
    print('Start sensors')
    main()