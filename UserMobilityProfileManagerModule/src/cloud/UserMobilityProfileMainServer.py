import _thread
import base64
import json
import logging
import socket
import threading
import time
import traceback
from tkinter import *
from tkinter import messagebox

from PIL import ImageTk, Image
import datetime
from tkinter.messagebox import showinfo
from bson import ObjectId

from cloud.UserIdentificationLogic import identify_user
from common.DatabaseConnector import *

MTU = 1024
CLOUD_IN_PORT = 55452
CLOUD_URL = '192.168.3.72'

# prendere dati da config file
config = configparser.ConfigParser()
path = Path(__file__).parent.parent.parent
config.read(os.path.join(path, 'files', 'configurations.ini'))
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


def open_db():
    client = MongoClient('mongodb://localhost:27017/')
    return client.UserProfileManagerDB


# Want ObjectId not the string of id
def get_user(user_id):
    db = open_db()
    return read_all_from_ump(ObjectId(user_id), db)


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
    result = modify_to_ump(user_id, db, field, value)
    return result


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

    user_id = identify_user(flag, db)
    if user_id is None:
        logging.info('User is not identified on Cloud')
        user = None
    else:
        user = get_user(user_id)

    os.remove(data_path)  # pulisce
    return user


class Server:
    def __init__(self, port, type, accept_function):
        logging.basicConfig(level=logging.INFO)
        self.port = port
        self.type = type
        self.accept_function = accept_function

    def setup(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((CLOUD_URL, self.port))
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


# ++++++++++++++++++++++++++++++++ Logica di comunicazione veicolo - cloud ++++++++++++++++++++++++++


def server_cloud_accept(server_socket):
    while True:
        logging.info("Cloud - T_accept : thread waiting connections")
        try:
            (client_socket, address) = server_socket.accept()
        except Exception:
            traceback.print_exc()
            logging.info("Cloud - T_accept : failing in accepting the connection")
            continue
        logging.info("Cloud - T_accept : new connection accepted from host -" + str(address) + "-")

        # creazione di un thread per gestire la ricezione dei dati dal veicolo
        recv_thread = threading.Thread(target=server_cloud_recv, args=(client_socket,))
        recv_thread.start()
        logging.info("Cloud - T_accept : created new thread for the recv of the sensor data")

    return


def server_cloud_recv(vehicle_socket):
    logging.info("Cloud - T_recv : wait for new buffer received from " + str(vehicle_socket))
    buffer = recv(vehicle_socket)

    logging.info("Cloud - T_recv : new buffer received ")
    logging.info(str(buffer))

    res = request_handler(buffer, vehicle_socket)

    if res:
        vehicle_socket.close()
        logging.info("Cloud - T_recv : closed socket with vehicle " + str(vehicle_socket))
        return
    res = update_handler(buffer, vehicle_socket)

    return res


cloud_server = Server(CLOUD_IN_PORT, "Cloud - Main", server_cloud_accept)


def return_remote_ump(inquiry_id, user, vehicle_socket):
    if user is not None:
        image = prepare_image(user['_id'])
        payload = {'inquiryID': inquiry_id, 'UMP': clean_dictionary(user), 'image': image}
    else:
        payload = {'inquiryID': inquiry_id, 'UMP': user}
    vehicle_socket.sendall(json.dumps(payload).encode('utf-8'))
    logging.info("Vehicle - T_recv : UMP successfully sended")
    return True


def prepare_image(user_id):
    print(str(user_id))
    file = open(os.path.join(KNOWN_FACES_DIR, str(user_id) + '_0.png'), 'rb')
    data_byte = file.read()
    return base64.encodebytes(data_byte).decode('utf-8')


def clean_dictionary(user):
    del user['image']
    del user['audio']
    user_id = user['_id']
    user['_id'] = str(user_id)
    return user


def request_remote_ump(inquiry_id, data_type, data):
    s = socket.socket()
    s.connect((CLOUD_URL, CLOUD_IN_PORT))

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
    except(Exception):
        logging.info("Cloud  : failed in parsing the data")
        return False

    if inquiry_id != inquiry_id:
        logging.info("Cloud  : The request identificator doesn't correspond")
        return None

    return ump


def request_handler(buffer, vehicle_socket):
    try:
        inquiry_id = buffer["inquiryID"]
        data_type = buffer["dataType"]
        data = buffer["data"]
    except Exception:
        logging.info("Cloud - T_recv  1: fail in parsing the data")
        return False

    logging.info("Cloud - T_recv : data successfully parsed")
    if data_type == 'modify':
        return False

    user = recognize_user(inquiry_id, data_type, base64.decodebytes(data.encode()))

    return return_remote_ump(inquiry_id, user, vehicle_socket)


def update_handler(buffer, vehicle_socket):
    try:
        print(buffer)
        inquiry_id = buffer["inquiryID"]
        datatype = buffer['dataType']
        ump = buffer['data']
    except Exception:
        logging.info("Cloud - T_recv  2: fail in parsing the data")
        return False

    logging.info("Cloud - T_recv : data successfully parsed")

    # bind con la parte di federico
    response = modify_fields_user(ObjectId(ump['_id']), ump['field'], ump['value'])
    if response.acknowledged is True:
        res = '1'
    else:
        res = '0'

    payload = {'inquiryID': inquiry_id, 'success_flag': res}

    vehicle_socket.sendall(json.dumps(payload).encode('utf-8'))
    logging.info("Vehicle - T_recv : UMP successfully sended")
    return True


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
        self.users = {}
        self.init_ui()
        self.i = 0
        self.images = []

    def edit(self, main_listbox, user_id, listbox, argumets):
        time = datetime.datetime.now()
        try:
            for argument in argumets:
                if argumets[argument].get():
                    if modify_fields_user(user_id, argument.cget('text').split(':')[0], argumets[argument].get()):
                        argument.configure(text="Name: " + argumets[argument].get())
                        self.users[user_id][argument.cget('text').split(':')[0]] = argumets[argument].get()
                        listbox.insert(END,
                                       str(time) + ": updated profile " + str(user_id) + " field name: " + argumets[
                                           argument].get())
                        main_listbox.insert(END,
                                            str(time) + ": updated profile " + str(user_id) + " field name: " +
                                            argumets[
                                                argument].get())
        except Exception:
            logging.info('Error to update user')
            main_listbox.insert(END, 'Error to update user')

    def populate_method(self, _id):
        self.listbox1.insert(END, str(datetime.datetime.now()) + ": opened profile: " + str(_id))
        if self.users[ObjectId(_id)]:
            self.open_profile(self.users[ObjectId(_id)])
        return False

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

    def open_edit(self, user, listbox, name, surname, age, gender, country, home_loc, job_loc):
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

        choices = ['male', 'female']
        variable = StringVar()
        variable.set('')

        Label(u_frame, font=('lato', 16), text="Gender :", anchor='w', bd=18, justify="left").grid(row=row, column=1)
        OptionMenu(u_frame, variable, *choices).grid(row=row, column=2)

        row += 1

        country_var = StringVar()
        country_var.set("")
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
        user_edit = {name: name_var, surname: surname_var, age: age_var, gender: variable, country: country_var,
                     home_loc: home_loc_var, job_loc: job_loc_var}

        Button(u_frame, text="Submit", font=('lato', 18), bd=18,
               command=combine_funcs(
                   (lambda user_id=user["_id"]: self.edit(self.listbox1, user_id, listbox, user_edit)),
                   t.destroy)).grid(row=row,
                                    column=1)

        Button(u_frame, text="Close", font=('lato', 18), bd=18, command=t.destroy).grid(row=row,
                                                                                        column=2)

    def open_profile(self, client):
        t = Toplevel(self)
        t.wm_title("User Mobility Profile - " + client["Name"] + " " + client["surname"])
        t.geometry("760x1200+150+300")

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

        try:
            im = Image.open(os.path.join(KNOWN_FACES_DIR, str(client['_id']) + '_0.png'))
            im = im.resize((100, 100), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(im)
            print("charging " + str(client['_id']))
            Button(self.canvas, text=str(client["Name"]) + " " + client[
                "surname"], image=photo, command=lambda m=str(client["_id"]): self.populate_method(m),
                   font=('lato', 18),
                   bd=18).grid(row=1, column=self.i)
            self.i += 1
            self.images.append(photo)
        except Exception:
            logging.error('Image not found')

    def add_user(self, user):
        if user['_id'] in self.users.keys():
            return False
        self.users[user['_id']] = user
        print(user)
        self.update_frame(user)
        self.listbox1.insert(END, str(datetime.datetime.now()) + ": added new user : " + user["Name"] + " " + user[
            "surname"])
        return True

    def listbox_insert(self, value):
        self.listbox1.insert(END, str(datetime.datetime.now()) + ":" + value)


def insert_all_users():
    db = open_db()
    users = get_all_users()
    read_all_images(db)
    for user in users:
        if app_gui.add_user(user) is False:
            print("Error")


def main():
    global app_gui
    root = Tk()
    root.geometry("560x560+300+300")
    app_gui = MainWindow()

    cloud_server.setup()
    time.sleep(2)
    _thread.start_new_thread(insert_all_users, ())

    try:
        root.mainloop()
    except Exception:
        print('error root')


if __name__ == '__main__':
    main()
