from UserIdentificationLogic import *
from DatabaseConnector import *
import configparser
import logging
from DatabaseConnector import read_all_audios
from os import listdir
from os.path import isfile, join

import acoustid
import chromaprint

from fuzzywuzzy import fuzz

config = configparser.ConfigParser()
path = Path(__file__).parent.parent
config.read(os.path.join(path, 'files', 'configurations.ini'))
setting = config['settings']


# TODO: Marsha and Andrea

def identify_user(data, flag, db):
    if flag == 1:
        logging.info('Start to elaborate a wav file')
        temp_res = []
        if data is None:
            logging.error('No file wav')
            return None

        mp3_files = get_all_audios(db)
        for song in mp3_files:
            res = match_audio(data, song)
            if res != 0:
                temp_res.append({'song': song, 'res': res})

        if temp_res is not []:
            best_res = get_best_result(temp_res)
        else:
            return None

        return best_res
    if flag == 0:
        # TODO: elaborazione immagini
        return

    return data  # todo: deve chiamare la funzione per il riconoscimento e restiruire
    #                 1 --> non trovato
    #                 id dell'utente


def get_best_result(results):
    best_perc = 0
    for result in results:
        temp = result['res']
        if temp > best_perc:
            best_perc = temp
            best_song = result['song']

    return best_song


def get_all_audios(db):
    if read_all_audios(db) == 1:
        logging.error('error to extract wav files')
        return

    only_files = [f for f in listdir(setting['sound_path']) if isfile(join(setting['sound_path'], f))]
    sounds = []
    for files in only_files:
        sounds.append(os.path.join(setting['sound_path'], files))

    return sounds


def match_audio(song1, song2):
    duration1, fp_encoded1 = acoustid.fingerprint_file(song1)
    duration2, fp_encoded2 = acoustid.fingerprint_file(song2)
    fingerprint1, version1 = chromaprint.decode_fingerprint(fp_encoded1)
    fingerprint2, version2 = chromaprint.decode_fingerprint(fp_encoded2)

    similarity = fuzz.ratio(fingerprint1, fingerprint2)
    print(similarity)

    if similarity >= 50:
        return similarity

    return 0
