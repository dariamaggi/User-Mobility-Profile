import os
import time
import pathlib
# import picamera
import socket
# from picamera import PiCamera

from CommandLayer import requestRemoteUMP


# CATTURA FOTO E SALVATAGGIO IN PNG  E INVIO SU SOCKET DEL PNG


def get_foto():
    camera = PiCamera()
    while 1 == 1:
        camera.start_preview()
        time.sleep(10)
        camera.capture(os.path.join(pathlib.Path(__file__), 'image.png'))
        camera.stop_preview()
