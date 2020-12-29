from pydub import AudioSegment

from UserIdentificationLogic import *
from DatabaseConnector import *
import configparser
import pydub
import numpy
import logging
from DatabaseConnector import read_all_audio
from os import listdir
from os.path import isfile, join

config = configparser.ConfigParser()
path = Path(__file__).parent.parent
config.read(os.path.join(path, 'files', 'configurations.ini'))
setting = config['settings']


# TODO: Marsha and Andrea

def identify_user(data, flag, db):
    if flag == 1:
        logging.info('Start to elaborate a mp3 file')
        mp3_files = []
        if mp3_files is None:
            logging.error('No file mp3')
            return False

        mp3_files = get_all_mp3_and_convert(db)
        for song in mp3_files:
            if matching_audio(data, song) is True:
                return True
        return False
    if flag == 0:
        # TODO: elaborazione immagini
        return

    return data  # todo: deve chiamare la funzione per il riconoscimento e restiruire
    #                 1 --> non trovato
    #                 id dell'utente


def get_all_mp3_and_convert(db):
    if read_all_audio(db) == 1:
        logging.error('error to extract mp3 files')
        return

    only_files = [f for f in listdir(setting['sound_path']) if isfile(join(setting['sound_path'], f))]
    sounds = []
    for files in only_files:
        sounds = convert_from_mp3_to_numpy(files)

    return sounds


# Funzione per conversione file mp3 del DB in numpy array #######################
# In file e first_audio e second_audio va il path del file mp3 in locale
def convert_from_mp3_to_numpy(file_mp3, normalized=False):
    """MP3 to numpy array"""
    try:
        #pydub.AudioSegment.ffmpeg = "/absolute/path/to/ffmpeg"
        a = pydub.AudioSegment.from_mp3('/Users/miucio/WorkSpaces/Pycharm/User-Mobility-Profile'
                                        '/UserMobilityProfileManagerModule/files/sounds/test1.mp3')
        # a = pydub.sound
        y = numpy.array(a.get_array_of_samples())
        if a.channels == 2:
            y = y.reshape((-1, 2))
        if normalized:
            return numpy.float32(y) / 2 ** 15
    except Exception:
        logging.error("Conversion Error", exc_info=True)

    return y


# Funzione per matching audio ##################################################
def matching_audio(first, second):
    c = numpy.in1d(first, second)
    count_true = 0

    for elem in c:
        if elem is True:
            count_true = count_true + 1

    if count_true >= ((c.size * 90) / 100):
        return True
    else:
        return False
