import base64
import time
from tkinter import messagebox
from tkinter.messagebox import showinfo
import json
import socket
import threading
import traceback
import datetime
import gridfs
from tkinter import *
from bson import ObjectId
import configparser
import logging
import face_recognition
import os
import acoustid
import chromaprint
from PIL import ImageTk, Image
from fuzzywuzzy import fuzz
from pymongo import MongoClient

# prendere dati da config file
config = configparser.ConfigParser()
config.read(os.path.join('/home/pi/Desktop/project/Car_controll', 'configurations.ini'))
setting = config['settings']

app_gui = ''
MTU = 1024
KNOWN_FACES_DIR = setting['img_path']
UNKNOWN_FACES_DIR = setting['temp_photo_path']
KNOWN_AUDIO_DIR = setting['sound_path']
UNKNOWN_AUDIO_DIR = setting['temp_sounds_path']
MONGOIP = setting['mongo_con']
TOLERANCE = 0.6
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = 'hog'  # default: 'hog', other one can be 'cnn' - CUDA accelerated (if available) deep-learning pretrained model
VEHICLE_IN_PORT = 65430
VEHICLE_URL = '192.168.1.211'

CLOUD_IN_PORT = 55452
CLOUD_URL = '192.168.3.72'


def open_db():
    client = MongoClient(MONGOIP)
    return client.UserProfileManagerDB


# Want ObjectId not the string of id
def get_user(user_id):
    db = open_db()
    return read_all_from_ump(user_id, db)


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
    print('try to modify:\nUser:' + str(user_id) + '\nField:' + field + '\nValue:' + value)
    result = modify_to_ump(user_id, db, field, value)
    if result.acknowledged is True:
        return modify_user_in_cloud(user_id, field, value)
    return result


# Want ObjectId not the string of id
# Write one image on files/sounds and return True False
# The Images format are user_id + .png
def get_image_by_id(user_id):
    db = open_db()
    user_photo = read_one_image_of_user(db, user_id)
    if user_photo is not None:
        output = open(os.path.join(KNOWN_FACES_DIR, str(user_id) + '.png'), 'wb')
        output.write(user_photo)
        output.close()

    return True


# Return a temp user and insert a temp user on db
def create_temp_user():
    db = open_db()
    list_fields = ['default', 'default', 'default', 43, 'default', 'default', 'default', 'default', 32,
                   'default', 98, 'default', 'default', 'default']
    user = create_user_json(list_fields)
    return create_user(db, user)


# request_id -> numero di richiesta(deve essere incrementale)
# data_type -> deve essere song o photo
# data -> foto o suono serializzato
def recognize_user(request_id, data_type, data):
    db = open_db()
    if data is None:
        return None

    if data_type == 'song':
        data_path = os.path.join(UNKNOWN_AUDIO_DIR, 'temp' + '.wav')
        flag = 1
    elif data_type == 'photo':
        data_path = os.path.join(UNKNOWN_FACES_DIR, 'temp' + '.png')
        flag = 0
    else:
        return False
    output = open(data_path, 'wb')
    output.write(data)
    output.close()

    app_gui.listbox_insert('Start recognize user')

    user_id = identify_user(flag, db)
    if user_id is None:
        logging.info('User is not identified on local')
        user = request_user_cloud(request_id, data_type, base64.encodebytes(data).decode('utf-8'))
        if user is None:
            logging.info('User is not identified on cloud, create temp user')
        else:
            logging.info('User identify')
            user_id = user['_id']
            user['_id'] = ObjectId(user_id)
    else:
        user = get_user(user_id)

    if user is not None:
        try:
            print(user)
            app_gui.listbox_insert('Start insert user')
            insert_user_in_gui(user)
            app_gui.listbox_insert('Created client')
        except:
            app_gui.listbox_insert('Error to create client')

    os.remove(data_path)  # pulisce
    return user_id


def insert_user_in_gui(client):
    try:
        get_image_by_id(client['_id'])
    except:
        print('Error to get image of client')
    if not app_gui.add_user(client):
        return False
    app_gui.listbox_insert('Insert user in GUI')
    return True


def modify_user_in_cloud(user_id, field, value):
    if request_remote_ump(1, 'modify', {'_id': str(user_id), 'field': field, 'value': value}):
        return True
    return False


def request_user_cloud(request_id, data_type, data):
    res = request_remote_ump(request_id, data_type, data)
    if not res:
        return None
    return res


# +++++++++++++++++++++       logica di Identificazione +++++++++++++++++++++++++++++++++++++++++++


# Find user
# Want flag--> 0=find by image,1=find by audio
# Return ObjectId client or None
# This function get the Unknown file on temp dir
def identify_user(flag, db):
    if not os.listdir(UNKNOWN_FACES_DIR) and not os.listdir(UNKNOWN_AUDIO_DIR)[0]:
        logging.error('No file')
        return None

    if flag == 1:
        app_gui.listbox_insert('Start to elaborate audio')
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
        app_gui.listbox_insert('Start to elaborate photo')
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

    if similarity >= 80:
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

        # But this time we assume that there might be more faces in an image - we can find faces of dirrerent people
        print(f', found {len(encodings)} face(s)')
        match = None
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


# # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#
# # ++++++++++++++++++++++++++++++++ Logica DB +++++++++++++++++++++++++++++++++++++++++++++++++++++++
#


def get_random_user(col):  # todo: ricorda di toglierlo
    return col.users.find_one()


# TODO: ricorda di gestire id di user mobility profile main logic differente dal db
def read_field_from_ump(user_id, col, field):
    return col.users.find_one({'_id': user_id}, {field: 1, '_id': 0})


def read_all_from_ump(user_id, col):
    return col.users.find_one({'_id': user_id})


def modify_to_ump(user_id, col, field, value):
    if field == 'image' or field == 'audio':
        return col.users.update_one({'_id': user_id},
                                    {'$push': {field: value}})

    return col.users.update_one({'_id': user_id},
                                {'$set': {field: value}})


def read_all_users(col):
    return col.users.find({})


def read_images_by_id(db, user_id):
    images = []
    fs = gridfs.GridFS(db)
    image_id = read_field_from_ump(user_id, db, 'image')
    if image_id is None:
        return 1
    for image in image_id['image']:
        try:
            images.append(fs.get(image).read())
        except Exception:
            print('Error to get image')

    return images
    return 1


def read_audios_by_id(db, user_id):
    audios = []
    fs = gridfs.GridFS(db)
    audio_id = read_field_from_ump(user_id, db, 'audio')
    if audio_id is []:
        return 1
    for audio in audio_id['audio']:
        try:
            audios.append(fs.get(audio).read())
        except Exception:
            print('Error to get audios')

    return audios


def read_one_image_of_user(col, user_id):
    try:
        images = read_images_by_id(col, user_id)
        if images is not None:
            return images[0]

        else:
            return None
    except:
        return None


def read_one_song_of_user(col, user_id):
    try:
        sounds = read_audios_by_id(col, user_id)
        if sounds is not None:
            return sounds[0]
        else:
            return None
    except:
        return None


def read_all_images(col):
    users = col.users.find().distinct('_id')
    try:
        for user in users:
            counter = 0
            images = read_images_by_id(col, user)
            for image in images:
                if image != 1:
                    output = open(os.path.join(KNOWN_FACES_DIR, str(user) + '_' + str(counter) + '.png'), 'wb')
                    output.write(image)
                    output.close()
                    counter = counter + 1
    except:
        return False

    return True


def read_all_audios(col):
    users = col.users.find().distinct('_id')
    try:
        for user in users:
            counter = 0
            audios = read_audios_by_id(col, user)
            for audio in audios:
                if audio != 1:
                    output = open(os.path.join(KNOWN_AUDIO_DIR, str(user) + '_' + str(counter) + '.wav'), 'wb')
                    output.write(audio)
                    output.close()
                    counter = counter + 1
    except:
        return False

    return True


def create_user(db, user):
    return db.users.insert_one(user)


def create_user_json(user):  # Use it only for test
    user_profile_manager_db = {
        'Name': user[0],
        'surname': user[1],
        'gender': user[2],
        'age': user[3],
        'country': user[4],
        'home_location': user[5],
        'job_location': user[6],
        'driving_style': user[7],
        'seat_inclination': user[8],
        'seat_orientation': user[9],
        'temperature_level': user[10],
        'light_level': user[11],
        'music_genres': user[12],
        'music_volume': user[13],
        # 'application_list': application_list[randint(0, (len(application_list) - 1))],
        # 'service_list': service_list[randint(0, (len(service_list) - 1))]
    }

    return user_profile_manager_db


# +++++++++++++++++++++       logica di comunicazione sensore - veicolo +++++++++++++++++++++++++++

class Server:
    def __init__(self, port, type, accept_function):
        logging.basicConfig(level=logging.INFO)
        self.port = port
        self.type = type
        self.accept_function = accept_function

    def setup(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), self.port))
        self.socket.listen(5)

        logging.info(str(self.type) + "  : server socket created")
        logging.info(self.socket)

        self.server = threading.Thread(target=self.accept_function, args=(self.socket,))
        self.server.start()
        logging.info(str(self.type) + "  : server accept thread started")
        return


def recv(socket):
    res = ""
    buffer = bytearray()
    b = socket.recv(MTU)
    while len(b) > 0:
        buffer = buffer + b
        try:
            res = json.loads(buffer.decode('utf-8'))
            break
        except Exception:
            b = socket.recv(MTU)
    return res


def server_vehicle_accept(server_socket):
    while True:
        logging.info("Vehicle - T_accept : thread waiting connections")
        try:
            (client_socket, address) = server_socket.accept()
        except (Exception):
            traceback.print_exc()
            logging.info("Vehicle - T_accept : failing in accepting the connection")
            continue

        logging.info("Vehicle - T_accept : new connection accepted from host -" + str(address) + "-")

        # creazione di un thread per gestire la ricezione dei dati dal sensore
        recv_thread = threading.Thread(target=server_vehicle_recv, args=(client_socket,))
        recv_thread.start()
        logging.info("Vehicle - T_accept : created new thread for the recv of the sensor data")

    return


def server_vehicle_recv(sensor_socket):
    logging.info("Vehicle - T_recv : wait for new buffer received from " + str(sensor_socket))

    buffer = recv(sensor_socket)

    logging.info("Vehicle - T_recv : new buffer received ")
    logging.info(str(buffer))

    try:
        request_id = buffer["requestID"]
        data_type = buffer["dataType"]
        data = buffer["data"]
    except Exception:
        logging.info("Vehicle - T_recv  : fail in parsing the data")
        return

    logging.info("Vehicle - T_recv : data successfully parsed")

    user_id = recognize_user(request_id, data_type, base64.decodebytes(data.encode()))

    return_user_identifier(request_id, str(user_id), sensor_socket)

    sensor_socket.close()
    logging.info("Vehicle - T_recv : chiusura socket di comunicazione con il sensore " + str(sensor_socket))

    return


# f chiamata dal veicolo per rispondere alla richiesta del sensore
def return_user_identifier(request_id, user_id, sensor_socket):
    payload = {'requestID': request_id, 'userID': user_id}

    sensor_socket.sendall(json.dumps(payload).encode('utf-8'))
    logging.info("Vehicle - T_recv : invio buffer al sensore avvenuto con successo")
    logging.info(str(payload))
    return


vehicle_server = Server(VEHICLE_IN_PORT, "Vehicle - Main", server_vehicle_accept)


# # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#
# # ++++++++++++++++++++++++++++++++ Logica di comunicazione veicolo - cloud ++++++++++++++++++++++++++
#


def request_remote_ump(inquiry_id, data_type, data):
    s = socket.socket()
    try:
        s.connect((CLOUD_URL, CLOUD_IN_PORT))
    except:
        print('Error to connect cloud')
        return False
    logging.info("Vehicle : socket to the cloud successfully created")
    payload = {'inquiryID': inquiry_id, 'dataType': data_type, 'data': data}

    # invio i dati
    s.sendall(json.dumps(payload).encode('utf-8'))

    logging.info("Cloud : request for UMP sended")

    buffer = recv(s)
    s.close()
    logging.info("Cloud : Response received, socket closed")
    try:
        inquiry_id = buffer["inquiryID"]
        ump = buffer["UMP"]

        if ump is not None:
            data = base64.decodebytes(buffer['image'].encode())
            data_path = os.path.join(KNOWN_FACES_DIR, ump['_id'] + '_0.png')
            output = open(data_path, 'wb')
            output.write(data)
            output.close()

    except(Exception):
        logging.info("Cloud  : failed in parsing the data")
        return False

    if inquiry_id != inquiry_id:
        logging.info("Cloud  : The request identificator doesn't correspond")
        return None
    return ump


# # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#
# # ++++++++++++++++++++++++++++++++ GUI++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def init_ui(info):
    print(info)


def on_click(event=None):
    # `command=` calls function without argument
    # `bind` calls function with one argument
    print("image clicked")


class UserProfile(Frame):
    def __init__(self, value):
        super().__init__()

        init_ui(value)


def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)

    return combined_func


def edit(main_listbox, user_id, client, listbox, name, arg1, surname, arg2, age, arg3, gender, arg4, country, arg5,
         home_loc, arg6, job_loc, arg7):
    time = datetime.datetime.now()
    try:
        if len(arg1.get()) != 0:
            result = modify_fields_user(user_id, "Name", arg1.get())
            if result:
                name.configure(text="Name: " + arg1.get())
                listbox.insert(END, str(time) + ": updated profile " + str(user_id) + " field name: " + arg1.get())
                main_listbox.insert(END, str(time) + ": updated profile " + str(user_id) + " field name: " + arg1.get())

        if len(arg2.get()) != 0:
            result = modify_fields_user(user_id, "surname", arg2.get())
            if result:
                surname.configure(text="Surname: " + arg2.get())
                listbox.insert(END, str(time) + ": updated profile " + str(user_id) + " field surname: " + arg2.get())
                main_listbox.insert(END,
                                    str(time) + ": updated profile " + str(user_id) + " field surname: " + arg2.get())

        if len(arg3.get()) != 0:
            try:
                int(str(arg3.get()))  # check if a number was actually entered
                result = modify_fields_user(user_id, "age", arg3.get())
                if result:
                    age.configure(text="Age: " + arg3.get())
                    listbox.insert(END, str(time) + ": updated profile " + str(user_id) + " field age: " + arg3.get())
                    main_listbox.insert(END,
                                        str(time) + ": updated profile " + str(user_id) + " field age: " + arg3.get())
            except ValueError:
                messagebox.showwarning(title=None, message="Age entered is not numeric.")

        if arg4.get() != "-":
            result = modify_fields_user(user_id, "gender", arg4.get())
            if result:
                gender.configure(text="Gender: " + arg4.get())
                listbox.insert(END, str(time) + ": updated profile " + str(user_id) + " field gender: " + arg4.get())
                main_listbox.insert(END,
                                    str(time) + ": updated profile " + str(user_id) + " field gender: " + arg4.get())

        if arg5.get() != "-":  # Country
            result = modify_fields_user(user_id, "country", arg5.get())
            if result:
                country.configure(text="Country: " + arg5.get())
                listbox.insert(END, str(time) + ": updated profile " + str(user_id) + " field country: " + arg5.get())
                main_listbox.insert(END,
                                    str(time) + ": updated profile " + str(user_id) + " field country: " + arg5.get())

        if len(arg6.get()) != 0:  # home location
            result = modify_fields_user(user_id, "home_location", arg6.get())
            if result:
                home_loc.configure(text="Home Location: " + arg6.get())
                listbox.insert(END,
                               str(time) + ": updated profile " + str(user_id) + " field home location: " + arg6.get())
                main_listbox.insert(END, str(time) + ": updated profile " + str(
                    user_id) + " field home location: " + arg6.get())

        if len(arg7.get()) != 0:  # job location
            result = modify_fields_user(user_id, "job location", arg7.get())
            if result:
                job_loc.configure(text="Home Location: " + arg7.get())

                listbox.insert(END,
                               str(time) + ": updated profile " + str(user_id) + " field job location: " + arg7.get())
                main_listbox.insert(END,
                                    str(time) + ": updated profile " + str(
                                        user_id) + " field job location: " + arg7.get())
    except Exception:
        logging.info('Error to update user')
        main_listbox.insert(END, 'Error to update user')


def get_field(client, field):
    if field in client.keys():
        return client[field]
    return ""


class MainWindow(Frame):

    def __init__(self):
        super().__init__()
        self.canvas = Canvas(self.master)

        self.labelframe1 = LabelFrame(self.master)
        self.frame = Frame(self.canvas)
        self.users = []
        self.init_ui()
        self.i = 0
        self.images = []

    def populate_method(self, user_id):
        self.listbox1.insert(END, str(datetime.datetime.now()) + ": opened profile: " + user_id)
        for user in self.users:
            if user["_id"] == ObjectId(user_id):
                self.open_profile(user)
        return

    def set_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def build_frames(self):

        left = Label(self.master, font=('lato', 18), text="Currently Loaded User Mobility Profiles", bd=18)
        left.pack()

        self.canvas.config(width=300, height=300)
        self.canvas.pack(side=TOP, expand=TRUE)

        # todo: attenzone a list_id --> client_id

        self.labelframe1.pack(expand="yes", fill=BOTH)
        Label(self.labelframe1, text="Console Log", font=('lato', 18), bg="white", bd=18).pack()
        vsb1 = Scrollbar(self.labelframe1, orient="vertical")

        self.listbox1 = Listbox(self.labelframe1, yscrollcommand=vsb1.set)
        vsb1.pack(side="right", fill="y")
        vsb1.config(command=self.listbox1.yview)

        self.listbox1.pack(expand="yes", fill=BOTH)

    def onselect(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.listbox_insert(value)
        self.open_profile(value)

    def init_ui(self):
        self.master.title("User Mobility Profile")
        self.build_frames()

    def about(self):
        showinfo("About",
                 "This project was made for the 2020/2021 edition of the Industrial Application course at the "
                 "University of Pisa.")
        self.master.update()

    def on_exit(self):
        self.quit()

    def open_edit(self, value, listbox, name, surname, age, gender, country, home_loc, job_loc):
        t = Toplevel(self)
        t.wm_title("Edit Profile")
        t.geometry("600x700+300+300")
        Label(t, font=('lato', 20), text="Edit profile", bd=18, justify="left").pack()

        u_frame = Frame(t)
        u_frame.pack()

        row = 2
        name_var = StringVar()
        name_lab = Label(u_frame, font=('lato', 16), text="Name :", anchor='w', bd=18, justify="left")
        name_lab.grid(row=row, column=1)

        name_entry = Entry(u_frame, textvariable=name_var)
        name_entry.grid(row=row, column=2)

        row += 1
        surname_var = StringVar()

        Label(u_frame, font=('lato', 16), text="Surname :", anchor='w', bd=18, justify="left").grid(
            row=row, column=1)
        entry_surname = Entry(u_frame, textvariable=surname_var)
        entry_surname.grid(row=row, column=2)

        row += 1
        age_var = StringVar()
        Label(u_frame, font=('lato', 16), text="Age :", anchor='w', bd=18, justify="left").grid(row=row, column=1)
        entry_age = Entry(u_frame, textvariable=age_var)
        entry_age.grid(row=row, column=2)

        checkCmd = IntVar()
        checkCmd.set(0)
        row += 1

        choices = ['-', 'male', 'female']
        variable = StringVar()
        variable.set('-')

        Label(u_frame, font=('lato', 16), text="Gender :", anchor='w', bd=18, justify="left").grid(row=row, column=1)
        OptionMenu(u_frame, variable, *choices).grid(row=row, column=2)

        row += 1

        country_var = StringVar()
        country_var.set("-")
        choice = ['Austria', 'Colombia', 'Italia']
        Label(u_frame, font=('lato', 16), text="Country:", anchor='w', bd=18, justify="left").grid(row=row, column=1)
        OptionMenu(u_frame, country_var, *choice).grid(row=row, column=2)
        home_loc_var = StringVar()
        job_loc_var = StringVar()
        Label(u_frame, font=('lato', 16), text="Home location:", anchor='w', bd=18, justify="left").grid(row=row,
                                                                                                         column=1)
        Entry(u_frame, textvariable=home_loc_var, ).grid(row=row, column=2)
        row += 1

        Label(u_frame, font=('lato', 16), text="Job location:", anchor='w', bd=18, justify="left").grid(row=row,
                                                                                                        column=1)
        Entry(u_frame, textvariable=job_loc_var, ).grid(row=row, column=2)

        row += 1

        Button(u_frame, text="Submit", font=('lato', 18), bd=18,
               command=combine_funcs(
                   (lambda user_id=value["_id"], client=value, listbox=listbox, nme=name, arg1=name_var,
                           srnme=surname,
                           arg2=surname_var, age=age,
                           arg3=age_var, gender=gender, arg4=variable, country=country, arg5=country_var,
                           home_loc=home_loc, arg6=home_loc_var,
                           job_loc=job_loc, arg7=job_loc_var
                    : edit(self.listbox1, user_id, client, listbox, nme, arg1, srnme,
                           arg2, age, arg3, gender, arg4, country, arg5,
                           home_loc, arg6, job_loc, arg7)), t.destroy)).grid(row=row,
                                                                             column=1)

        Button(u_frame, text="Close", font=('lato', 18), bd=18, command=t.destroy).grid(row=row,
                                                                                        column=2)

    def open_profile(self, client):
        t = Toplevel(self)
        print(client)
        t.wm_title("User Mobility Profile - " + client["Name"] + " " + client["surname"])
        t.geometry("1200x800+150+300")

        u_frame = LabelFrame(t)

        left = Label(u_frame, font=('lato', 18), text="User Profile -" + client["Name"] + " " + client["surname"],
                     bd=18)
        left.grid(row=2, column=2)
        canvas1 = Canvas(u_frame)

        # id = client['_id']
        canvas1.grid(row=4, column=1, padx=10)
        # call procedure to populate canvas

        lbl_name = Label(canvas1, font=('lato', 16), text="Name: " + get_field(client, 'Name'), anchor='w',
                         bd=18,
                         justify="left")
        lbl_name.pack()
        lbl_surname = Label(canvas1, font=('lato', 16), text="Surname: " + get_field(client, 'surname'),
                            anchor='w',
                            bd=18, justify="left")
        lbl_surname.pack()
        lbl_age = Label(canvas1, font=('lato', 16), text="Age: " + str(get_field(client, 'age')), anchor='w', bd=18,
                        justify="left")
        lbl_age.pack()
        lbl_gender = Label(canvas1, font=('lato', 16), text="Gender: " + get_field(client, 'gender'), anchor='w',
                           bd=18,
                           justify="left")
        lbl_gender.pack()
        lbl_country = Label(canvas1, font=('lato', 16), text="Country: " + get_field(client, 'country'),
                            anchor='w',
                            bd=18, justify="left")
        lbl_country.pack()
        canvas2 = Canvas(u_frame)
        canvas2.grid(row=4, column=2)
        lbl_homeloc = Label(canvas2, font=('lato', 16),
                            text="Home Location: " + get_field(client, 'home_location'),
                            anchor='w', bd=18, justify="left")
        lbl_homeloc.pack()
        lbl_jobloc = Label(canvas2, font=('lato', 16), text="Job Location: " + get_field(client, 'job_location'),
                           anchor='w', bd=18, justify="left")
        lbl_jobloc.pack()
        lbl_lochistory = Label(canvas2, font=('lato', 16),
                               text="Location History: " + get_field(client, 'location_history'), anchor='w',
                               bd=18,
                               justify="left")
        lbl_lochistory.pack()
        lbl_drivingstyle = Label(canvas2, font=('lato', 16),
                                 text="Driving Style: " + get_field(client, 'driving_style'),
                                 anchor='w', bd=18, justify="left")
        lbl_drivingstyle.pack()
        lbl_seatincl = Label(canvas2, font=('lato', 16),
                             text="Seat Inclination: " + str(get_field(client, 'seat_inclination')), anchor='w',
                             bd=18,
                             justify="left")
        lbl_seatincl.pack()
        canvas3 = Canvas(u_frame)
        canvas3.grid(row=4, column=3)
        lbl_seator = Label(canvas3, font=('lato', 16),
                           text="Seat Orientation: " + get_field(client, "seat_orientation"),
                           anchor='w', bd=18, justify="left")
        lbl_seator.pack()
        lbl_temp = Label(canvas3, font=('lato', 16),
                         text="Temperature: " + str(get_field(client, 'temperature_level')),
                         anchor='w', bd=18, justify="left")
        lbl_temp.pack()
        lbl_lightlevel = Label(canvas3, font=('lato', 16),
                               text="Light Level: " + get_field(client, 'light_level'),
                               anchor='w', bd=18, justify="left")
        lbl_lightlevel.pack()
        lbl_musicgenres = Label(canvas3, font=('lato', 16),
                                text="Music Genres: " + get_field(client, 'music_genres'),
                                anchor='w', bd=18, justify="left")
        lbl_musicgenres.pack()
        lbl_musicvolume = Label(canvas3, font=('lato', 16),
                                text="Music Volume: " + get_field(client, 'music_volume'),
                                anchor='w', bd=18, justify="left")
        lbl_musicvolume.pack()
        listbox_applications = Listbox(u_frame)
        listbox_applications.config(height=0)
        Label(u_frame, font=('lato', 16),
              text="Application List: ",
              anchor='w', bd=18, justify="left").grid(row=5, column=1)
        listbox_applications.grid(row=5, column=2)
        for item in client["application_list"]:
            listbox_applications.insert(END, item)
        Label(u_frame, font=('lato', 16),
              text="Application List: ",
              anchor='w', bd=18, justify="left").grid(row=6, column=1)

        listbox_services = Listbox(u_frame)
        listbox_services.config(height=0)

        listbox_services.grid(row=6, column=2)

        for item in client["service_list"]:
            listbox_services.insert(END, item)

        u_frame.pack(fill="both", expand="yes")
        # label with image
        l_frame = LabelFrame(t)
        l_frame.pack(fill="both", expand="yes")

        right = Label(l_frame, font=('lato', 18), text="Console Log", bd=18)
        right.pack()
        vsb1 = Scrollbar(l_frame, orient="vertical")

        listbox1 = Listbox(l_frame, yscrollcommand=vsb1.set)

        vsb1.pack(side="right", fill="y")
        vsb1.config(command=listbox1.yview)

        listbox1.pack(expand="yes", fill=BOTH)

        [listbox1.insert(END, " " + elem) for elem in self.listbox1.get(0, self.listbox1.size() - 1)]
        Button(l_frame, text="Edit", font=('lato', 18),
               command=lambda name=lbl_name, surname=lbl_surname, age=lbl_age, gender=lbl_gender,
                              country=lbl_country, home_loc=lbl_homeloc, job_loc=lbl_jobloc,
                              app_list=listbox_applications,
                              serv_list=listbox_services: self.open_edit(client,
                                                                         listbox1,
                                                                         name,
                                                                         surname,
                                                                         age, gender,
                                                                         country,
                                                                         home_loc,
                                                                         job_loc)).pack()

    def update_frame(self, client):

        im = Image.open(os.path.join(KNOWN_FACES_DIR, str(client['_id']) + '_0.png'))
        im = im.resize((100, 100), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(im)
        print("charging " + str(client['_id']))
        Button(self.canvas, text=str(client["Name"]) + " " + client[
            "surname"], image=photo, command=lambda m=str(client["_id"]): self.populate_method(m), font=('lato', 18),
               bd=18).grid(row=1, column=self.i)
        self.i += 1
        self.images.append(photo)

    def add_user(self, user):
        for item in self.users:
            if user["_id"] == item["_id"]:
                return False

        self.users.append(user)
        print(user)
        self.update_frame(user)
        self.listbox1.insert(END, str(datetime.datetime.now()) + ": added new user : " + user["Name"] + " " + user[
            "surname"])
        return True

    def listbox_insert(self, value):
        self.listbox1.insert(END, str(datetime.datetime.now()) + ":" + value)


def clean_folder():
    for f in os.listdir(KNOWN_FACES_DIR):
        os.remove(os.path.join(KNOWN_FACES_DIR, f))

    for f in os.listdir(UNKNOWN_FACES_DIR):
        os.remove(os.path.join(UNKNOWN_FACES_DIR, f))

    for f in os.listdir(KNOWN_AUDIO_DIR):
        os.remove(os.path.join(KNOWN_AUDIO_DIR, f))

    for f in os.listdir(UNKNOWN_AUDIO_DIR):
        os.remove(os.path.join(UNKNOWN_AUDIO_DIR, f))

    print('Clean all folder')


def main():
    global app_gui

    clean_folder()

    root = Tk()
    root.geometry("560x560+300+300")
    app_gui = MainWindow()

    vehicle_server.setup()

    try:
        root.mainloop()
    except Exception:
        print('error root')


if __name__ == '__main__':
    main()
