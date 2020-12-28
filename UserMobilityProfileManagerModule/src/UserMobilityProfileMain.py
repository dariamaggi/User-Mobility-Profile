from bson import ObjectId
from interface.config_file import *
from UserIdentificationLogic import *

from DatabaseConnector import *

# prendere dati da config file
config = configparser.ConfigParser()
config.read('configurations.ini')
setting = config['settings']


def open_db():
    client = MongoClient('mongodb://127.0.0.1:27017')
    return client.UserProfileManagerDB


def get_user(user_id):  # Want ObjectId not the string of id
    db = open_db()
    return read_all_from_ump(ObjectId(user_id), db)


def get_field_of_user(user_id, field):  # Want ObjectId not the string of id
    db = open_db()
    return read_field_from_ump(ObjectId(user_id), db, field)


def get_all_users():
    db = open_db()
    users = []
    collection = read_all_users(db)
    for user in collection:
        users.append(user)

    return users


def modify_fields_user(user_id, field, value):  # Want ObjectId not the string of id
    db = open_db()
    return modify_to_ump(user_id, db, field, value)


def get_all_image():
    db = open_db()
    return read_all_images(db)


def get_all_audio():
    db = open_db()
    return read_all_audio(db)


def get_image_by_id(user_id):  # Want ObjectId not the string of id
    db = open_db()
    user_photo = read_image_by_id(db, user_id)
    output = open(str(user_id) + '.jpg', 'wb')
    output.write(user_photo)
    output.close()


def get_audio_by_id(user_id):  # Want ObjectId not the string of id
    db = open_db()
    user_audio = read_audio_by_id(db, user_id)
    output = open(str(user_id) + '.mp3', 'wb')
    output.write(user_audio)
    output.close()


def create_temp_user():
    db = open_db()
    list_fields = ['default', 'default', 'default', 43, 'default', 'default', 'default', 'default', 32,
                   'default', 98, 'default', 'default', 'default']
    user = create_user_json(list_fields)
    return create_user(db, user)


def delete_user_by_id(user_id):  # Want ObjectId not the string of id
    db = open_db()
    return delete_user(user_id,db)  # Return DeleteResult


def get_user(request_id, data_type, data):
    user = identify_user(data)
    response = []
    if user is 1:
        #user = request_remote_ump(data)
        if user is 1:
            user = create_temp_user()

    response.insert(data['request_id'], user['_id'])
    return response


# TODO: da definire con Marsha e Andrea
def insert_user(user):
    create_user(user)
