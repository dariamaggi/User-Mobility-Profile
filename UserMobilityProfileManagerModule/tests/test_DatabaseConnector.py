from unittest import TestCase

from bson import ObjectId

from DatabaseConnector import *


def open_db():
    client = MongoClient('mongodb://127.0.0.1:27017')
    return client.UserProfileManagerDB


class Test(TestCase):
    def test_rundb(self):
        self.run()


# class Test(TestCase):
#     def test_populate_db(self):
#         self.run()
#
#
# class Test(TestCase):
#     def test_insert_image(self):
#         _client = MongoClient('mongodb://127.0.0.1:27017')
#         db = _client.UserProfileManagerDB
#         res = insert_file(db, sys.argv[2],'5fe4caecae8c2795230cc132')
#         self.assertIsNotNone(res, 'error')
class Test(TestCase):
    def test_read_field_from_ump(self):
        db = open_db()
        name = read_field_from_ump(ObjectId('5fe760722de6b440735e340b'), db, 'Name')
        self.assertIsNotNone(name, "Errore read from ump")

    def test_read_all_from_ump(self):
        db = open_db()
        collection = read_all_from_ump(ObjectId('5fe760722de6b440735e340b'), db)
        self.assertIsNotNone(collection, "Errore read from ump")

    def test_modify_to_ump(self):
        self.fail()

    def test_insert_user(self):
        self.fail()

    def test_delete_user(self):
        self.fail()

    def test_insert_image(self):
        self.fail()

    def test_insert_audio(self):
        self.fail()

    def test_get_image_by_id(self):
        self.fail()

    def test_get_audio_by_id(self):
        self.fail()

    def test_insert_file(self):
        self.fail()

    def test_get_all_images(self):
        self.fail()

    def test_populate_db(self):
        self.fail()
