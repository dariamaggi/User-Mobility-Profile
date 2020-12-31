import time
import picamera
import socket
from picamera import PiCamera

# CATTURA FOTO E SALVATAGGIO IN PNG  E INVIO SU SOCKET DEL PNG
camera = PiCamera()

camera.start_preview()
time.sleep(10)
camera.capture('/home/pi/image.png')
camera.stop_preview()