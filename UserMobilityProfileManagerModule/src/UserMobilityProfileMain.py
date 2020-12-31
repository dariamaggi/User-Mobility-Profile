from bson import ObjectId
from UserIdentificationLogic import *

from DatabaseConnector import *

# prendere dati da config file
config = configparser.ConfigParser()
path = Path(__file__).parent.parent
config.read(os.path.join(path, 'files', 'configurations.ini'))
setting = config['settings']


def open_db():
    client = MongoClient(setting['mongo_con'])
    return client.UserProfileManagerDB


# Want ObjectId not the string of id
def get_user(user_id):
    db = open_db()
    return read_all_from_ump(ObjectId(user_id), db)


# Want ObjectId not the string of id
def get_field_of_user(user_id, field):
    db = open_db()
    return read_field_from_ump(ObjectId(user_id), db, field)


# Return Collection of users
def get_all_users():
    db = open_db()
    users = []
    collection = read_all_users(db)
    for user in collection:
        users.append(user)

    return users


# Want ObjectId not the string of id
def modify_fields_user(user_id, field, value):
    db = open_db()
    return modify_to_ump(user_id, db, field, value)


# Write all images on files/photos and return True False
# The Images format are user_id + _ + counter(incremental) + .png
def get_all_image():
    db = open_db()
    return read_all_images(db)


# Write all sounds on files/sounds and return True False
# The Sounds format are user_id + _ + counter(incremental) + .mp3
def get_all_audio():
    db = open_db()
    return read_all_audios(db)


# Want ObjectId not the string of id
# Write all images on files/sounds and return True False
# The Images format are user_id + _ + counter(incremental) + .png
def get_images_by_id(user_id):
    db = open_db()
    counter = 0
    user_photos = read_images_by_id(db, user_id)
    if user_photos is None:
        return False
    for photo in user_photos:
        if photo is not None:
            output = open(os.path.join(setting['img_path'], str(user_id) + '_' + counter + '.png'), 'wb')
            output.write(photo)
            output.close()
            counter = counter + 1

    return True


# Want ObjectId not the string of id
# Write one image on files/sounds and return True False
# The Images format are user_id + .png
def get_image_by_id(user_id):
    db = open_db()
    user_photo = read_one_image_of_user(db, user_id)
    output = open(os.path.join(setting['img_path'], str(user_id) + '.png'), 'wb')
    output.write(user_photo[0])
    output.close()

    return True


# Want ObjectId not the string of id
# Write all images on files/sounds and return True False
# The Images format are user_id + _ + counter(incremental) + .mp3
def get_audios_by_id(user_id):
    db = open_db()
    counter = 0
    user_audios = read_audios_by_id(db, user_id)
    if user_audios is None:
        return False
    for audio in user_audios:
        if audio is not None:
            output = open(os.path.join(setting['sound_path'], str(user_id) + '_' + counter + '.mp3'), 'wb')
            output.write(audio)
            output.close()
            counter = counter + 1

    return True


# Want ObjectId not the string of id
# Write one audio on files/sounds and return True False
# The audio format is user_id + .mp3
def get_audio_by_id(user_id):
    db = open_db()
    user_audio = read_one_song_of_user(db, user_id)
    output = open(os.path.join(setting['sound_path'], str(user_id) + '.mp3'), 'wb')
    output.write(user_audio)
    output.close()


# Return a temp user and insert a temp user on db
def create_temp_user():
    db = open_db()
    list_fields = ['default', 'default', 'default', 43, 'default', 'default', 'default', 'default', 32,
                   'default', 98, 'default', 'default', 'default']
    user = create_user_json(list_fields)
    return create_user(db, user)


# Want ObjectId not the string of id
# Return DeleteResult
def delete_user_by_id(user_id):
    db = open_db()
    return delete_user(user_id, db)


def get_user_temp_non_usare(request_id, data_type, data):
    user = identify_user(data)
    response = []
    if user is 1:
        # user = request_remote_ump(data)
        if user is 1:
            user = create_temp_user()

    response.insert(data['request_id'], user['_id'])
    return response


# TODO: da definire con Marsha e Andrea
def insert_user(user):
    create_user(user)
