import threading
import time
import logging
from CameraLogic import get_foto
import MicLogic


def thread_function(name):
    logging.info("Thread %s: starting", name)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)


def main():
    """Entry point for the application script"""

    thread_function(target=get_foto())

    print("Call your main application code here")
