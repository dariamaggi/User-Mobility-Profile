import os
from tkinter import *
from tkinter import messagebox

from PIL import ImageTk, Image
from PIL import Image as PImage
import datetime
from tkinter.messagebox import showinfo
from json import loads
from UserMobilityProfileMainClient import modify_fields_user, get_image_by_id

FOLDERPATH = ''


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


def edit(main_listbox, user_id, client, listbox, name, arg1, surname, arg2, age, arg3, gender, arg4, country, arg5,
         home_loc,
         arg6, job_loc, arg7, app_list, arg8, serv_list, arg9):
    time = datetime.datetime.now()
    if len(arg1.get()) != 0:
        result = modify_fields_user(id, "name", arg1.get())
        if result:
            name.configure(text="Name: " + arg1.get())
            listbox.insert(END, str(time) + ": updated profile " + user_id + " field name: " + arg1.get())
            main_listbox.insert(END, str(time) + ": updated profile " + user_id + " field name: " + arg1.get())

    if len(arg2.get()) != 0:
        result = modify_fields_user(id, "surname", arg2.get())
        if result:
            surname.configure(text="Surname: " + arg2.get())
            listbox.insert(END, str(time) + ": updated profile " + user_id + " field surname: " + arg2.get())
            main_listbox.insert(END, str(time) + ": updated profile " + user_id + " field surname: " + arg2.get())

    if len(arg3.get()) != 0:
        try:
            int(str(arg3.get()))  # check if a number was actually entered
            result = modify_fields_user(id, "age", arg3.get())
            if result:
                age.configure(text="Age: " + arg3.get())
                listbox.insert(END, str(time) + ": updated profile " + user_id + " field age: " + arg3.get())
                main_listbox.insert(END, str(time) + ": updated profile " + user_id + " field age: " + arg3.get())
        except ValueError:
            messagebox.showwarning(title=None, message="Age entered is not numeric.")

    if arg4.get() != "-":
        result = modify_fields_user(id, "gender", arg4.get())
        if result:
            gender.configure(text="Gender: " + arg4.get())
            listbox.insert(END, str(time) + ": updated profile " + user_id + " field gender: " + arg4.get())
            main_listbox.insert(END, str(time) + ": updated profile " + user_id + " field gender: " + arg4.get())

    if arg5.get() != "-":  # Country
        result = modify_fields_user(id, "country", arg5.get())
        if result:
            country.configure(text="Country: " + arg5.get())
            listbox.insert(END, str(time) + ": updated profile " + user_id + " field country: " + arg5.get())
            main_listbox.insert(END, str(time) + ": updated profile " + user_id + " field country: " + arg5.get())

    if len(arg6.get()) != 0:  # home location
        result = modify_fields_user(id, "home_location", arg6.get())
        if result:
            home_loc.configure(text="Home Location: " + arg6.get())
            listbox.insert(END, str(time) + ": updated profile " + user_id + " field home location: " + arg6.get())
            main_listbox.insert(END, str(time) + ": updated profile " + user_id + " field home location: " + arg6.get())

    if len(arg7.get()) != 0:  # job location
        result = modify_fields_user(id, "job location", arg7.get())
        if result:
            job_loc.configure(text="Home Location: " + arg7.get())

            listbox.insert(END, str(time) + ": updated profile " + user_id + " field job location: " + arg7.get())
            main_listbox.insert(END,
                                str(time) + ": updated profile " + user_id + " field job location: " + arg7.get())

    if len(arg8.get()) != 0:
        new_elements = arg8.get().split(",")

        result = modify_fields_user(id, "application_list", arg8.get())

        if result:
            app_list = [app_list.delete(idx) for idx in range(app_list.size())]
            for new_item in new_elements:
                app_list.insert(END, new_item)


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

    def populate_method(self, method):
        self.listbox1.insert(END, str(datetime.datetime.now()) + ": opened profile: " + str(method))
        client = ""
        for item in self.users:
            if item["_id"] == method:
                client = item
                break
        self.open_profile(client)

    def set_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def build_frames(self):

        left = Label(self.master, font=('lato', 18), text="Currently Loaded User Mobility Profiles", bd=18)
        left.pack()

        vbar = Scrollbar(self.canvas, orient=VERTICAL)
        vbar.pack(side=RIGHT, fill=Y)
        vbar.config(command=self.canvas.yview)
        self.canvas.config(width=300, height=300)
        self.canvas.config(yscrollcommand=vbar.set)

        self.canvas.pack(side=TOP, expand=TRUE)

        i = 1
        # paths=FOLDERPATH
        # todo: attenzone a list_id --> client_id
        client_ids = [item["_id"] for item in self.users]
        [get_image_by_id(id) for id in client_ids]  # adds the images to the folder

        path = FOLDERPATH  # TODO: add path to folder

        for client_id in client_ids:
            im = Image.open(os.path.join(path, str(client_id) + '.png'))
            im = im.resize((100, 100), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(im)
            label = Label(self.canvas, text=client_id, image=photo, compound="top", font=('lato', 18), bd=18)
            label.bind('<Button-1>', lambda m=client_id: self.populate_method(m))
            label.pack()

        self.frame.bind('<Configure>', self.set_scrollregion)

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

    def open_edit(self, value, listbox, name, surname, age, gender, country, home_loc, job_loc, app_list, serv_list):
        t = Toplevel(self)
        t.wm_title("Edit Profile")
        t.geometry("400x560+300+300")
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
        Label(u_frame, font=('lato', 16), text="Application List:", anchor='w', bd=18, justify="left").grid(row=row,
                                                                                                            column=1)

        app_list_var = StringVar()

        txt = Text(u_frame, textvariable=app_list_var)
        for val in value["application_list"]:
            txt.insert(END, val + ",")

        row += 1
        Label(u_frame, font=('lato', 16), text="Service List:", anchor='w', bd=18, justify="left").grid(row=row,
                                                                                                        column=1)

        serv_list_var = StringVar()

        txt1 = Text(u_frame, textvariable=serv_list_var)
        for val in value["application_list"]:
            txt1.insert(END, val + ",")

        row += 1

        Button(t, text="Submit",
               command=lambda user_id=value["_id"], client=value, listbox=listbox, nme=name, arg1=name_var,
                              srnme=surname,
                              arg2=surname_var, age=age,
                              arg3=age_var, gender=gender, arg4=variable, country=country, arg5=country_var,
                              home_loc=home_loc, arg6=home_loc_var,
                              job_loc=job_loc, arg7=job_loc_var, app_list=app_list, arg8=app_list_var,
                              serv_list=serv_list, arg9=serv_list_var
               : edit(self.listbox1, user_id, client, listbox, nme, arg1, srnme,
                      arg2, age, arg3, gender, arg4, country, arg5,
                      home_loc, arg6, job_loc, arg7, app_list, arg8, serv_list, arg9)).pack()

        Button(t, text="Close", command=t.destroy).pack()

    def open_profile(self, client):
        t = Toplevel(self)
        t.wm_title("User Mobility Profile - " + client["Name"] + " " + client["surname"])
        t.geometry("760x660+250+300")
        path = FOLDERPATH  # TODO: inserire il path

        u_frame = LabelFrame(t)
        left = Label(u_frame, font=('lato', 18), text="User Profile -" + client["Name"] + " " + client["surname"],
                     bd=18)
        left.grid(row=2, column=2)
        im = Image.open(os.path.join(path, str(client["_id"]) + '.png'))
        im = im.resize((200, 200), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(im)
        label = Label(u_frame, image=photo)
        label.grid(row=3, column=2)

        canvas1 = Canvas(u_frame)

        # id = client['_id']
        canvas1.grid(row=4, column=1, padx=10)
        # call procedure to populate canvas

        lbl_name = Label(canvas1, font=('lato', 16), text="Name: " + get_field(client, 'name'), anchor='w',
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
        listbox_applications.pack()
        for item in client["application_list"]:
            listbox_applications.insert(END, item)

        listbox_services = Listbox(u_frame)
        listbox_services.pack()

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
        Button(u_frame, text="Edit", font=('lato', 18),
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
                                                                         job_loc,
                                                                         app_list,
                                                                         serv_list)).grid(
            row=2, column=3)

    def update_frame(self, client):

        get_image_by_id(client["_id"])

        path = FOLDERPATH  # TODO: inserire il path

        im = Image.open(os.path.join(path, str(client['_id']) + '.png'))
        im = im.resize((100, 100), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(im)
        Button(self.canvas, text=client["_id"], compound="top",
               command=lambda m=client["_id"]: self.populate_method(m), font=('lato', 18), bd=18).pack()

    def add_user(self, client):
        for item in self.users:
            if client["_id"] is item["_id"]:
                return False
        self.users.append(client)
        self.update_frame(client)
        self.listbox1.insert(END, str(datetime.datetime.now()) + ": added new user : " + client["Name"] + " " + client[
            "surname"])
        return True

    def listbox_insert(self, value):
        self.listbox1.insert(END, str(datetime.datetime.now()) + ":" + value)


def main():
    root = Tk()
    root.geometry("560x560+300+300")

    app = MainWindow()  # todo: ricorda che devi chiamare il metodo di questa classe
    root.mainloop()


if __name__ == '__main__':
    main()
