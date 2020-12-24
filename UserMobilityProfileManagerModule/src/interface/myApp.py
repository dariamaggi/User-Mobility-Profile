from tkinter import *

import datetime
from tkinter.messagebox import showinfo



class MainWindow(Frame):

    def __init__(self):
        super().__init__()

        self.initUI()


    def buildFrames(self):

        self.labelframe = LabelFrame(self.master, text= "Currently Loaded User Mobility Profiles")
        self.labelframe.pack(fill="both", expand="yes")
        left = Label(self.labelframe)
        left.pack()

        self.labelframe1 = LabelFrame(self.master, text= "Console Log")
        self.labelframe1.pack(fill="both", expand="yes")

        vsb = Scrollbar(self.labelframe, orient="vertical")
        vsb1 = Scrollbar(self.labelframe1, orient="vertical")

        self.listbox = Listbox(self.labelframe, yscrollcommand=vsb.set)
        [self.listbox.insert(END, "value"+str(i)) for i in range(19)]
        self.listbox1 = Listbox(self.labelframe1,  yscrollcommand=vsb1.set)


        vsb.pack(side="right", fill="y")
        vsb.config(command=self.listbox.yview)

        vsb1.pack(side="right", fill="y")
        vsb1.config(command=self.listbox1.yview)

        self.listbox1.pack(expand="yes", fill=BOTH)

        self.listbox.configure(justify=CENTER)
        self.listbox.pack(expand="yes", fill=BOTH)

        self.listbox.bind('<<ListboxSelect>>', self.onselect)
        right = Label(self.labelframe1)
        right.pack()


    def listbox_insert(self, value):
        self.listbox1.insert(END, str(datetime.datetime.now())+":"+"You opened user profile: "+value)

    def onselect(self, evt):

        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.listbox_insert(value)
        self.create_window(value)


    def initUI(self):

        self.master.title("User Mobility Profile")
        self.buildFrames()
        self.buildMenu()

    def about(self):
        showinfo("About","This project was made for the 2020/2021 edition of the Industrial Application course at the University of Pisa.")
        self.master.update()
    def addUser(self):
        showinfo("Add user","This has not been implemented yet.")

    def buildMenu(self):

        menubar = Menu(self.master)
        self.master.config(menu = menubar)

        options= Menu(menubar)
        options.add_command(label = "Add user", command = self.addUser)

        menubar.add_cascade(label = "Options", menu = options)

        filemenu = Menu(menubar)
        filemenu.add_command(label = "Exit", command = self.onExit)
        filemenu.add_command(label = "About", command = self.about)

        menubar.add_cascade(label = "Help", menu = filemenu)


    def onExit(self):

        self.quit()

    def create_window(self, value):
        self.counter = 1
        t = Toplevel(self)
        t.wm_title("User Mobility Profile - "+ value)
        t.geometry("560x560+350+300")


#      l = Label(t, text="This is window #%s" % self.counter)
  #      l.pack(side="top", fill="both", expand=True, padx=100, pady=100)



def main():

    root = Tk()
    root.geometry("560x560+300+300")
    app = MainWindow()
    root.mainloop()


if __name__ == '__main__':
    main()