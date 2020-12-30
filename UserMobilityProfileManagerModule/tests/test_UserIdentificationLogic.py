from unittest import TestCase
from UserIdentificationLogic import *


def open_db():
    client = MongoClient('mongodb://127.0.0.1:27017')
    return client.UserProfileManagerDB


class Test(TestCase):

    def test_get_all_mp3(self):
        db = open_db()
        sounds = get_all_mp3(db)
        self.assertIsNotNone(sounds, 'Errore estrazione file mp3')

    def test_match_audio(self):
        db = open_db()
        sounds = get_all_mp3(db)
        flag = match_audio(sounds[0], sounds[4])
        self.assertTrue(flag, 'Errore match audio')

    def test_identify_user(self):
        db = open_db()
        sounds = get_all_mp3(db)
        user = identify_user(sounds[0], 1, db)
        self.assertIsNotNone(user, 'Nessun utente trovato')
