import time
from bson import ObjectId
from common.DatabaseConnector import *
import configparser
import logging
import face_recognition
import os
import acoustid
import chromaprint

from fuzzywuzzy import fuzz

config = configparser.ConfigParser()
path = Path(__file__).parent.parent.parent
config.read('/Users/miucio/WorkSpaces/Pycharm/User-Mobility-Profile/UserMobilityProfileManagerModule/files/configurations.ini')
setting = config['settings']

KNOWN_FACES_DIR = setting['img_path']
UNKNOWN_FACES_DIR = setting['temp_photo_path']
KNOWN_AUDIO_DIR = setting['sound_path']
UNKNOWN_AUDIO_DIR = setting['temp_sounds_path']
MONGOIP = setting['mongo_con']
TOLERANCE = 0.6
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = 'hog'  # default: 'hog', other one can be 'cnn' - CUDA accelerated (if available) deep-learning pretrained model


# Find user
# Want flag--> 0=find by image,1=find by audio
# Return ObjectId client or None
# This function get the Unknown file on temp dir
def identify_user(flag, db):
    if not os.listdir(UNKNOWN_FACES_DIR) and not os.listdir(UNKNOWN_AUDIO_DIR)[0]:
        logging.error('No file')
        return None

    if flag == 1:
        logging.info('Start to elaborate a wav file')
        temp_res = []

        if read_all_audios(db) is False:
            logging.error('error to extract wav files')
            return
        start_time = time.time()
        for filename in os.listdir(KNOWN_AUDIO_DIR):
            res = match_audio(os.path.join(UNKNOWN_AUDIO_DIR, os.listdir(UNKNOWN_AUDIO_DIR)[0]),
                              os.path.join(KNOWN_AUDIO_DIR, filename))
            if res != 0:
                temp_res.append({'song': filename, 'res': res})

        if not temp_res:
            print('No results')
            print("--- %s seconds ---" % (time.time() - start_time))
            return None
        else:
            best_res = get_best_result(temp_res)
            print('best result is' + best_res)
            print("--- %s seconds ---" % (time.time() - start_time))

    if flag == 0:
        if read_all_images(db) is False:
            logging.error('error to extract png files')
            return None
        start_time = time.time()
        best_res = search_face()
        print("--- %s seconds ---" % (time.time() - start_time))
        if best_res is None:
            return None

    return ObjectId(best_res.split('.')[0].split('_')[0])



def get_best_result(results):
    best_perc = 0
    for result in results:
        temp = result['res']
        if temp > best_perc:
            best_perc = temp
            best_song = result['song']

    return best_song


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


def search_face():
    print('Loading known faces...')
    known_faces = []
    known_names = []

    # We oranize known faces as subfolders of KNOWN_FACES_DIR
    # Each subfolder's name becomes our label (name)
    for name in os.listdir(KNOWN_FACES_DIR):

        # Next we load every file of faces of known person
        # for filename in os.listdir(f'{KNOWN_FACES_DIR}/{name}'):

        # Load an image
        image = face_recognition.load_image_file(f'{KNOWN_FACES_DIR}/{name}')

        # Get 128-dimension face encoding Always returns a list of found faces, for this purpose we take first face
        # only (assuming one face per image as you can't be twice on one image)
        try:
            encoding = face_recognition.face_encodings(image)[0]
            # Append encodings and name
            known_faces.append(encoding)
            known_names.append(name)
            print(f'Known Faces: Filename {name} \n', end='')

        except Exception as e:
            print(f"Error to encode image: {KNOWN_FACES_DIR}/{name} \n {e}")
            pass

    print('Processing unknown faces...')
    # Now let's loop over a folder of faces we want to label
    for filename in os.listdir(UNKNOWN_FACES_DIR):
        # Load image
        print(f'Unknown Faces: Filename {filename}', end='')
        image = face_recognition.load_image_file(f'{UNKNOWN_FACES_DIR}/{filename}')

        # This time we first grab face locations - we'll need them to draw boxes
        locations = face_recognition.face_locations(image, model=MODEL)

        # Now since we know loctions, we can pass them to face_encodings as second argument
        # Without that it will search for faces once again slowing down whole process
        encodings = face_recognition.face_encodings(image, locations)
        match = None
        # But this time we assume that there might be more faces in an image - we can find faces of dirrerent people
        print(f', found {len(encodings)} face(s)')
        for face_encoding, face_location in zip(encodings, locations):

            # We use compare_faces (but might use face_distance as well)
            # Returns array of True/False values in order of passed known_faces
            results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)

            # Since order is being preserved, we check if any face was found then grab index
            # then label (name) of first matching known face withing a tolerance

            print(results)
            if True in results:  # If at least one is true, get a name of first of found labels
                match = known_names[results.index(True)]
                return match

        return match
