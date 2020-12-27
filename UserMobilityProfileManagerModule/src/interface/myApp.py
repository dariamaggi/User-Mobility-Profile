from tkinter import *
from PIL import ImageTk, Image
import datetime
from tkinter.messagebox import showinfo
from json import loads

class UserProfile(Frame):
    def __init__(self, value):
        super().__init__()

        self.initUI(value)

    def initUI(self, info):
        print(info)

class MainWindow(Frame):

    def __init__(self):
        super().__init__()
        self.users=[]
        self.initUI()

    def populateMethod(self, method):
        self.listbox1.insert(END, str(datetime.datetime.now())+": opened profile: "+ method)
        self.openProfile(method)

    def set_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    def buildFrames(self):
        left = Label(self.master, font=('lato', 18), text="Currently Loaded User Mobility Profiles", bd=18)
        left.pack()

        self.canvas = Canvas(self.master)
        self.canvas.pack(side=TOP, expand=TRUE)

        i=1
        for method in ["Lucas", "John", "Bob"]:
            button = Button(self.canvas, text=method,
                            command=lambda m=method: self.populateMethod(m),font=('lato', 18), bd=18)
            button.grid(row=0,column=i)
            i+=1
            if i%3==0:
                i=0
                button = Button(self.canvas, text=method,
                                command=lambda m=method: self.populateMethod(m), font=('lato', 18), bd=18)
                button.grid(row=1, column=i)


        self.frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor=NW)
        self.frame.bind('<Configure>', self.set_scrollregion)


        self.labelframe1=LabelFrame(self.master)
        self.labelframe1.pack(expand="yes", fill=BOTH)
        title= Label(self.labelframe1,text="Console Log", font=('lato', 18), bd=18).pack()
        vsb1 = Scrollbar(self.labelframe1, orient="vertical")

        self.listbox1 = Listbox(self.labelframe1,yscrollcommand=vsb1.set)
        vsb1.pack(side="right", fill="y")
        vsb1.config(command=self.listbox1.yview)

        self.listbox1.pack(expand="yes", fill=BOTH)


    def listbox_insert(self, value):
        self.listbox1.insert(END, str(datetime.datetime.now())+":"+"You opened user profile: "+value)

    def onselect(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.listbox_insert(value)
        self.openProfile(value)

    def initUI(self):
        self.master.title("User Mobility Profile")
        self.buildFrames()

    def about(self):
        showinfo("About","This project was made for the 2020/2021 edition of the Industrial Application course at the University of Pisa.")
        self.master.update()

    def onExit(self):
        self.quit()
    def readfromUMP(self, value):
        return value

    def openProfile(self, value):
        t = Toplevel(self)
        t.wm_title("User Mobility Profile - "+ value)
        t.geometry("760x660+350+300")

        u_frame= LabelFrame(t)
        left = Label(u_frame, font=('lato', 18), text="User Profile -" + value, bd=18)
        left.grid(row=2, column=2)
        Button(u_frame, text="Edit", font=('lato', 18)).grid (row=2, column=3)
        Image=Label(u_frame,font=('lato', 18), text=self.readfromUMP('ProfileImage'), bd=18, justify="left" ).grid(row=3, column=2)

        canvas1 = Canvas(u_frame)

        canvas1.grid(row=4, column=1, padx=10)
        #call procedure to populate canvas

        lbl_name = Label(canvas1,font=('lato', 16),  text="Name: "+self.readfromUMP('Name'), anchor='w',bd=18,justify="left"  )
        lbl_name.pack()

        lbl_surname = Label(canvas1,font=('lato', 16),text="Surname: "+self.readfromUMP('Surname'), anchor='w',bd=18,justify="left"  )
        lbl_surname.pack()

        lbl_age=Label(canvas1,font=('lato', 16),  text="Age: "+self.readfromUMP('Age'), anchor='w',bd=18,justify="left"  )
        lbl_age.pack()

        lbl_gender=Label(canvas1,font=('lato', 16), text="Gender: "+self.readfromUMP('Gender'),anchor='w',bd=18,justify="left"  )
        lbl_gender.pack()

        lbl_country=Label(canvas1,font=('lato', 16),text="Country: "+self.readfromUMP('Country'), anchor='w',bd=18,justify="left"  )
        lbl_country.pack()

        canvas2 = Canvas(u_frame)
        canvas2.grid(row=4, column=2)

        lbl_homeloc=Label(canvas2,font=('lato', 16), text="Home Location: "+self.readfromUMP('home_location'), anchor='w', bd=18,justify="left"  )
        lbl_homeloc.pack()

        lbl_jobloc=Label(canvas2,font=('lato', 16), text="Job Location: "+self.readfromUMP('job_location'),   anchor='w',bd=18,justify="left"  )
        lbl_jobloc.pack()

        lbl_lochistory = Label(canvas2,font=('lato', 16), text="Location History: "+self.readfromUMP('Location History'), anchor='w', bd=18,justify="left"  )
        lbl_lochistory.pack()

        lbl_drivingstyle=Label(canvas2,font=('lato', 16), text="Driving Style: "+self.readfromUMP('driving_style'), anchor='w', bd=18,justify="left"  )
        lbl_drivingstyle.pack()

        lbl_seatincl=Label(canvas2,font=('lato', 16), text="Seat Inclination: "+self.readfromUMP('seat_inclination'), anchor='w',bd=18,justify="left"  )
        lbl_seatincl.pack()

        canvas3 = Canvas(u_frame)
        canvas3.grid(row=4, column=3)

        lbl_seator=Label(canvas3,font=('lato', 16), text="Seat Orientation: "+self.readfromUMP('home_location'), anchor='w',bd=18,justify="left"  )
        lbl_seator.pack()

        lbl_temp=Label(canvas3,font=('lato', 16), text="Temperature: "+self.readfromUMP('temperature_level'),  anchor='w',bd=18,justify="left"  )
        lbl_temp.pack()

        lbl_lightlevel=Label(canvas3,font=('lato', 16), text="Location History: "+self.readfromUMP('light_level'), anchor='w',bd=18,justify="left"  )
        lbl_lightlevel.pack()

        lbl_musicgenres=Label(canvas3,font=('lato', 16), text="Music Genres: "+self.readfromUMP('music_genres'),anchor='w',bd=18,justify="left"  )
        lbl_musicgenres.pack()

        lbl_musicvolume=Label(canvas3,font=('lato', 16), text="Music Volume: "+self.readfromUMP('music_volume'), anchor='w',bd=18,justify="left"  )
        lbl_musicvolume.pack()
        u_frame.pack(fill="both", expand="yes")



        # label with image
        l_frame= LabelFrame(t)
        l_frame.pack(fill="both", expand="yes")

        right = Label(l_frame, font=('lato', 18), text="Console Log",  bd=18)
        right.pack()
        vsb1 = Scrollbar(l_frame, orient="vertical")


        listbox1 = Listbox(l_frame, yscrollcommand=vsb1.set)


        vsb1.pack(side="right", fill="y")
        vsb1.config(command=listbox1.yview)

        listbox1.pack(expand="yes", fill=BOTH)

        [listbox1.insert(END, " "+elem) for elem in  self.listbox1.get(0, self.listbox1.size() - 1)]

        #TODO: handle image

def main():

    root = Tk()
    root.geometry("560x560+300+300")

    app = MainWindow()
    root.mainloop()


if __name__ == '__main__':
    main()