from common.DatabaseConnector import *
import configparser
import logging
from os import listdir
from os.path import isfile, join
#import face_recognition
import os
#import cv2
import acoustid
import chromaprint

from fuzzywuzzy import fuzz
config = configparser.ConfigParser()
path = Path(__file__).parent.parent.parent
config.read(os.path.join(path, 'files', 'configurations.ini'))
setting = config['settings']

KNOWN_FACES_DIR = 'known_faces'
UNKNOWN_FACES_DIR = 'unknown_faces'
TOLERANCE = 0.6
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = 'hog'  # default: 'hog', other one can be 'cnn' - CUDA accelerated (if available) deep-learning pretrained model


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


# Returns (R, G, B) from name
def name_to_color(name):
    # Take 3 first letters, tolower()
    # lowercased character ord() value rage is 97 to 122, substract 97, multiply by 8
    color = [(ord(c.lower()) - 97) * 8 for c in name[:3]]
    return color


known_faces = []
known_names = []


# def encode_photos(folder):
#     print('Known faces')
#     # Each subfolder's name becomes our label (name)
#     for name in os.listdir(folder):
#
#         # Next we load every file of faces of known person
#         for filename in os.listdir(f'{folder}/{name}'):
#
#             # Load an image
#             image = face_recognition.load_image_file(f'{folder}/{name}/{filename}')
#
#             try:
#                 encoding = face_recognition.face_encodings(image)[0]
#                 # Append encodings and name
#                 known_faces.append(encoding)
#                 known_names.append(name)
#                 print(f'Known Faces: Filename {filename} \n', end='')
#
#             except Exception as e:
#                 print(f"Error to encode image: {folder}/{name}/{filename} \n {e}")
#                 pass
#
#     return known_faces, known_names
#
#
# def face_recognice(image):
#     # This time we first grab face locations - we'll need them to draw boxes
#     locations = face_recognition.face_locations(image, model=MODEL)
#
#     # Now since we know loctions, we can pass them to face_encodings as second argument
#     # Without that it will search for faces once again slowing down whole process
#     encodings = face_recognition.face_encodings(image, locations)
#
#     # We passed our image through face_locations and face_encodings, so we can modify it
#     # First we need to convert it from RGB to BGR as we are going to work with cv2
#     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#
#     # But this time we assume that there might be more faces in an image - we can find faces of dirrerent people
#     print(f', found {len(encodings)} face(s)')
#     for face_encoding, face_location in zip(encodings, locations):
#
#         # We use compare_faces (but might use face_distance as well)
#         # Returns array of True/False values in order of passed known_faces
#         results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
#
#         # Since order is being preserved, we check if any face was found then grab index
#         # then label (name) of first matching known face withing a tolerance
#         match = None
#
#         if True in results:  # If at least one is true, get a name of first of found labels
#             match = known_names[results.index(True)]
#
#             # Each location contains positions in order: top, right, bottom, left
#             top_left = (face_location[3], face_location[0])
#             bottom_right = (face_location[1], face_location[2])
#
#             # Get color by name using our fancy function
#             color = name_to_color(match)
#
#             # Paint frame
#             cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)
#
#             # Now we need smaller, filled grame below for a name
#             # This time we use bottom in both corners - to start from bottom and move 50 pixels down
#             top_left = (face_location[3], face_location[2])
#             bottom_right = (face_location[1], face_location[2] + 22)
#
#             # Paint frame
#             cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
#
#             # Wite a name
#             cv2.putText(image, match, (face_location[3] + 10, face_location[2] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
#                         (200, 200, 200), FONT_THICKNESS)
#
#         return match
#
#
# def from_unknown_folder(folder):
#     # Now let's loop over a folder of faces we want to label
#     for filename in os.listdir(folder):
#         # Load image
#         print(f'Unknown Faces: Filename {filename}', end='')
#         image = face_recognition.load_image_file(f'{folder}/{filename}')
#         match = face_recognice(image)
#         print(match)

#
# encode_photos(KNOWN_FACES_DIR)
# from_unknown_folder(UNKNOWN_FACES_DIR)