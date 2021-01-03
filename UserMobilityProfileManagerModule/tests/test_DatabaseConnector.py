import sys
from unittest import TestCase

from car.DatabaseConnector import *


def open_db():
    client = MongoClient('mongodb://127.0.0.1:27017')
    return client.UserProfileManagerDB


class Test(TestCase):
    def test_populate_db(self):
        populate_db()

    def test_get_random_user(self):
        db = open_db()
        user = get_random_user(db)
        self.assertIsNotNone(user, "Error get random user from ump")

    def test_read_all_users(self):
        db = open_db()
        users = read_all_users(db)
        for document in users:
            print(document)
        self.assertIsNotNone(users, "Error get all users from ump")

    def test_read_field_from_ump(self):
        db = open_db()
        user = get_random_user(db)
        name = read_field_from_ump(user['_id'], db, 'Name')
        self.assertIsNotNone(name, "Error read field from ump")

    def test_read_all_from_ump(self):
        db = open_db()
        user = get_random_user(db)
        collection = read_all_from_ump(user['_id'], db)
        self.assertIsNotNone(collection, "Error read all from ump")

    def test_modify_to_ump(self):
        db = open_db()
        user = get_random_user(db)
        result = modify_to_ump(user['_id'], db, 'job_location', 'test')
        self.assertTrue(result.acknowledged, "Error modify from ump")
        modify_to_ump(user['_id'], db, 'job_location', "none")

    def test_insert_user(self):
        db = open_db()
        list_fields = ['federico', 'pippo', 'test', 43, 'pippo', 'test', 'federico', 'pippo', 32,
                       'federico', 98, 'test', 'federico', 'pippo']
        user = create_user_json(list_fields)
        return_of_call = create_user(db, user)
        self.assertIsNotNone(return_of_call, "Error create user")

    def test_delete_user(self):
        db = open_db()
        user = get_random_user(db)
        result = delete_user(user['_id'], db)
        self.assertTrue(result.acknowledged, "Error delete user from ump")
        insert_user(db, user)

    def test_insert_file(self):
        db = open_db()
        result = insert_file(db, sys.argv[2])
        self.assertIsNotNone(result, "Error insert file")

    def test_insert_image(self):
        db = open_db()
        user = get_random_user(db)
        result = insert_image(db, sys.argv[2], user['_id'])
        self.assertTrue(result.acknowledged, "Error insert image")

    def test_read_image_by_id(self):
        db = open_db()
        user = get_random_user(db)
        result = read_images_by_id(db, user['_id'])
        self.assertIsNotNone(result, "Error get image")

    def test_read_all_images(self):
        db = open_db()
        result = read_all_images(db)
        self.assertEqual(result, 0, "Error get all image")

    def test_insert_audio(self):
        db = open_db()
        user = get_random_user(db)
        result = insert_audio(db, sys.argv[3], user['_id'])
        self.assertTrue(result.acknowledged, "Error insert audio")

    def test_read_audio_by_id(self):
        db = open_db()
        user = get_random_user(db)
        result = read_audios_by_id(db, user['_id'])
        self.assertIsNotNone(result, "Error get audio")

    def test_read_all_audio(self):
        db = open_db()
        result = read_all_audios(db)
        self.assertEqual(result, 0, "Error get all audio")

    def test_read_one_image_of_user(self):
        db = open_db()
        user = get_random_user(db)
        result = read_one_image_of_user(db, user['_id'])
        self.assertIsNotNone(result, 'Error to get one image')
