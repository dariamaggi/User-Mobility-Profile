import os
from tkinter import *
from PIL import ImageTk, Image
from PIL import Image as PImage
import datetime
from tkinter.messagebox import showinfo
from json import loads


def init_ui(info):
    print(info)


class UserProfile(Frame):
    def __init__(self, value):
        super().__init__()

        init_ui(value)


def load_images(path):
    # return array of images

    images_list = os.listdir(path)
    loaded_images = []
    for image in images_list:
        img = PImage.open(path + image)
        loaded_images.append(img)


def edit(name, arg1):
    name.configure(text=arg1)
    print(arg1)


def read_from_ump(value):
    return value


class MainWindow(Frame):

    def __init__(self):
        super().__init__()
        self.canvas = Canvas(self.master)
        self.labelframe1 = LabelFrame(self.master)
        self.frame = Frame(self.canvas)
        self.users = []
        self.init_ui()

    def populate_method(self, method):
        self.listbox1.insert(END, str(datetime.datetime.now()) + ": opened profile: " + method)
        self.open_profile(method)

    def set_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def build_frames(self):
        left = Label(self.master, font=('lato', 18), text="Currently Loaded User Mobility Profiles", bd=18)
        left.pack()
        self.canvas.pack(side=TOP, expand=TRUE)

        i = 1

        for method in ["id_0", "id_1"]:
            # button = Button(self.canvas, text=method,image=img,command=lambda m=method: self.populateMethod(m),
            # font=('lato', 18), bd=18)
            button = Button(self.canvas, text=method, command=lambda m=method: self.populate_method(m),
                            font=('lato', 18), bd=18)
            button.grid(row=0, column=i)
            i += 1

        self.canvas.create_window((0, 0), window=self.frame, anchor=NW)
        self.frame.bind('<Configure>', self.set_scrollregion)

        self.labelframe1.pack(expand="yes", fill=BOTH)
        title = Label(self.labelframe1, text="Console Log", font=('lato', 18), bg="white", bd=18).pack()
        vsb1 = Scrollbar(self.labelframe1, orient="vertical")

        self.listbox1 = Listbox(self.labelframe1, yscrollcommand=vsb1.set)
        vsb1.pack(side="right", fill="y")
        vsb1.config(command=self.listbox1.yview)

        self.listbox1.pack(expand="yes", fill=BOTH)

    def listbox_insert(self, value):
        self.listbox1.insert(END, str(datetime.datetime.now()) + ":" + "You opened user profile: " + value)

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

    def open_edit(self, name, surname):
        t = Toplevel(self)
        t.wm_title("Edit Profile")
        t.geometry("400x460+350+300")
        Label(t, font=('lato', 20), text="Edit profile", bd=18, justify="left").pack()

        u_frame = Frame(t)
        u_frame.pack()

        row = 2

        name_lab = Label(u_frame, font=('lato', 16), text="Name :", anchor='w', bd=18, justify="left")
        name_lab.grid(row=row, column=1)

        name_entry = Entry(u_frame)
        name_entry.insert(0, read_from_ump("Name"))
        name_entry.grid(row=row, column=2)

        row += 1
        lbl_surname = Label(u_frame, font=('lato', 16), text="Surname :", anchor='w', bd=18, justify="left").grid(
            row=row, column=1)
        entry_surname = Entry(u_frame)
        entry_surname.insert(0, read_from_ump("Surname"))
        entry_surname.grid(row=row, column=2)

        row += 1
        Label(u_frame, font=('lato', 16), text="Age :", anchor='w', bd=18, justify="left").grid(row=row, column=1)
        entry_age = Entry(u_frame)
        entry_age.insert(0, read_from_ump("Age"))
        entry_age.grid(row=row, column=2)

        Button(t, text="ubmit", command=lambda nme=name, arg1=name_entry.get(): edit(nme, arg1)).pack()

    def open_profile(self, value):
        t = Toplevel(self)
        t.wm_title("User Mobility Profile - " + value)
        t.geometry("760x660+350+300")
        path = ""#TODO: inserire il path del cuore

        im = Image.open(path)
        photo = ImageTk.PhotoImage(im)

        label = Label(t, image=photo)
        label.image = photo  # keep a reference!
        label.pack()

        u_frame = LabelFrame(t)
        left = Label(u_frame, font=('lato', 18), text="User Profile -" + value, bd=18)
        left.grid(row=2, column=2)

        canvas1 = Canvas(u_frame)

        canvas1.grid(row=4, column=1, padx=10)
        # call procedure to populate canvas

        lbl_name = Label(canvas1, font=('lato', 16), text="Name: " + read_from_ump('Name'), anchor='w', bd=18,
                         justify="left")
        lbl_name.pack()

        lbl_surname = Label(canvas1, font=('lato', 16), text="Surname: " + read_from_ump('Surname'), anchor='w',
                            bd=18, justify="left")
        lbl_surname.pack()

        lbl_age = Label(canvas1, font=('lato', 16), text="Age: " + read_from_ump('Age'), anchor='w', bd=18,
                        justify="left")
        lbl_age.pack()

        lbl_gender = Label(canvas1, font=('lato', 16), text="Gender: " + read_from_ump('Gender'), anchor='w', bd=18,
                           justify="left")
        lbl_gender.pack()

        lbl_country = Label(canvas1, font=('lato', 16), text="Country: " + read_from_ump('Country'), anchor='w',
                            bd=18, justify="left")
        lbl_country.pack()

        canvas2 = Canvas(u_frame)
        canvas2.grid(row=4, column=2)

        lbl_homeloc = Label(canvas2, font=('lato', 16), text="Home Location: " + read_from_ump('home_location'),
                            anchor='w', bd=18, justify="left")
        lbl_homeloc.pack()

        lbl_jobloc = Label(canvas2, font=('lato', 16), text="Job Location: " + read_from_ump('job_location'),
                           anchor='w', bd=18, justify="left")
        lbl_jobloc.pack()

        lbl_lochistory = Label(canvas2, font=('lato', 16),
                               text="Location History: " + read_from_ump('Location History'), anchor='w', bd=18,
                               justify="left")
        lbl_lochistory.pack()

        lbl_drivingstyle = Label(canvas2, font=('lato', 16), text="Driving Style: " + read_from_ump('driving_style'),
                                 anchor='w', bd=18, justify="left")
        lbl_drivingstyle.pack()

        lbl_seatincl = Label(canvas2, font=('lato', 16),
                             text="Seat Inclination: " + read_from_ump('seat_inclination'), anchor='w', bd=18,
                             justify="left")
        lbl_seatincl.pack()

        canvas3 = Canvas(u_frame)
        canvas3.grid(row=4, column=3)

        lbl_seator = Label(canvas3, font=('lato', 16), text="Seat Orientation: " + read_from_ump('home_location'),
                           anchor='w', bd=18, justify="left")
        lbl_seator.pack()

        lbl_temp = Label(canvas3, font=('lato', 16), text="Temperature: " + read_from_ump('temperature_level'),
                         anchor='w', bd=18, justify="left")
        lbl_temp.pack()

        lbl_lightlevel = Label(canvas3, font=('lato', 16), text="Location History: " + read_from_ump('light_level'),
                               anchor='w', bd=18, justify="left")
        lbl_lightlevel.pack()

        lbl_musicgenres = Label(canvas3, font=('lato', 16), text="Music Genres: " + read_from_ump('music_genres'),
                                anchor='w', bd=18, justify="left")
        lbl_musicgenres.pack()

        lbl_musicvolume = Label(canvas3, font=('lato', 16), text="Music Volume: " + read_from_ump('music_volume'),
                                anchor='w', bd=18, justify="left")
        lbl_musicvolume.pack()
        u_frame.pack(fill="both", expand="yes")
        Button(u_frame, text="Edit", font=('lato', 18),
               command=lambda name=lbl_name, surname=lbl_surname: self.open_edit(name, surname)).grid(row=2, column=3)

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

        # TODO: handle image


def main():
    root = Tk()
    root.geometry("560x560+300+300")

    app = MainWindow()
    root.mainloop()


if __name__ == '__main__':
    main()
