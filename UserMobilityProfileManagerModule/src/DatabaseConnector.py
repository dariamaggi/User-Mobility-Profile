from pymongo import MongoClient
from random import randint
from PIL import Image
import io


def rundb():
    _client = MongoClient('mongodb://127.0.0.1:27017')
    db = _client.UserProfileManagerDB


# TODO: ricorda di gestire id di user mobility profile main logic differente dal db
def read_from_ump(user_id, col, field):
    return col.users.find({'_id': user_id}, {field: 1, '_id': 0})


def modify_to_ump(user_id, col, field, value):
    return col.users.update_one({'id': user_id}, {field: value})


def insert_user(col, value):
    return col.users.insert_one(value)  # Return the ID


def delete_user(user_id, col):
    return col.users.delete_one({'_id': user_id})


def insert_image(user_id, col, image_dir):
    im = Image.open(image_dir)
    image_bytes = io.BytesIO()
    im.save(image_bytes, format='PNG')
    image_id = col.images.insert_one(image_bytes.getvalue())

    return modify_to_ump(user_id, col, 'image', image_id)


def get_all_images(col):
    return col.images.find({})
    #READ AN IMM
    # pil_img = Image.open(io.BytesIO(image['data']))
    # plt.imshow(pil_img)
    # plt.show()


def populate_db():
    client = MongoClient('mongodb://127.0.0.1:27017')  # Open DB
    db = client.UserProfileManagerDB  # Define DB

    mycol = db["users"]  # Get collection
    mycol.drop()  # Clean collection

    names = ['Guido', 'Federico', 'Riccardo', 'Daria', 'Marsha', 'Andrea']
    surname = ['Bertini', 'Lapenna']
    gender = ['Male', 'Female']
    age = [25, 28, 22, 23]
    country = ['Italian', 'Puerto Rico']
    home_location = ['Campo', 'Ozieri']
    job_location = ['none']
    driving_style = ['Sport', 'Normal']
    seat_inclination = [30, 31, 32, 27]
    seat_orientation = ['Frontal']
    temperature_level = [25, 26, 27, 28, 29]
    light_level = ['low', 'medium', 'high']
    music_genres = ['Metal', 'rap']
    music_volume = ['moderate', 'high']
    application_list = [{'Facebook', 'youtube'}, {'Facebook', 'Telegram'}, {'Instagram', 'youtube'}]
    service_list = [{'Amazon prime', 'Netflix'}, {'Sky', 'Netflix'}]

    for x in range(1, 3):
        user_profile_manager_db = {
            'Name': names[randint(0, (len(names) - 1))],
            'surname': surname[randint(0, (len(surname) - 1))],
            'gender': gender[randint(0, (len(gender) - 1))],
            'age': age[randint(0, (len(age) - 1))],
            'country': country[randint(0, (len(country) - 1))],
            'home_location': home_location[randint(0, (len(home_location) - 1))],
            'job_location': job_location[randint(0, (len(job_location) - 1))],
            'driving_style': driving_style[randint(0, (len(driving_style) - 1))],
            'seat_inclination': seat_inclination[randint(0, (len(seat_inclination) - 1))],
            'seat_orientation': seat_orientation[randint(0, (len(seat_orientation) - 1))],
            'temperature_level': temperature_level[randint(0, (len(temperature_level) - 1))],
            'light_level': light_level[randint(0, (len(light_level) - 1))],
            'music_genres': music_genres[randint(0, (len(music_genres) - 1))],
            'music_volume': music_volume[randint(0, (len(music_volume) - 1))],
            # 'application_list': application_list[randint(0, (len(application_list) - 1))],
            # 'service_list': service_list[randint(0, (len(service_list) - 1))]
        }
        # Step 3: Insert business object directly into MongoDB via isnert_one
        result = db.users.insert_one(user_profile_manager_db)
        # Step 4: Print to the console the ObjectID of the new document
        print('Created {0} of 500 as {1}'.format(x, result.inserted_id))
    # Step 5: Tell us that you are done
    print('finished creating 500 business reviews')
