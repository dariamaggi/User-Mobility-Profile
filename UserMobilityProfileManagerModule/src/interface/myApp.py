from tkinter import *

import datetime

class Example(Frame):

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
        right = Label(self.labelframe)
        right.pack()


    def listbox_insert(self, value):
        self.listbox1.insert(END, str(datetime.datetime.now())+":"+"You opened user profile: "+value)

    def onselect(self, evt):

        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.listbox_insert(value)

    def setMenu(self):
        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="File", menu=fileMenu)
    def initUI(self):

        self.master.title("User Mobility Profile")
        self.buildFrames()



    def onExit(self):

        self.quit()


def main():

    root = Tk()
    root.geometry("560x560+300+300")
    app = Example()
    root.mainloop()


if __name__ == '__main__':
    main()