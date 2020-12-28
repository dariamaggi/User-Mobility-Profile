from bson import ObjectId
from pymongo import MongoClient

from DatabaseConnector import *


def open_db():
    client = MongoClient('mongodb://127.0.0.1:27017')
    return client.UserProfileManagerDB


def get_user(user_id):
    db = open_db()
    return read_all_from_ump(ObjectId(user_id), db)


def get_field_of_user(user_id, field):
    db = open_db()
    return read_field_from_ump(ObjectId(user_id), db, field)


def get_all_users():
    db = open_db()
    users = []
    collection = read_all_users(db)
    for user in collection:
        users.append(user)

    return users


def modify_fields_user(user_id, field, value):
    db = open_db()
    return modify_to_ump(user_id, db, field, value)


# TODO: da definire con Marsha e Andrea
def insert_user(user):
    create_user(user)
