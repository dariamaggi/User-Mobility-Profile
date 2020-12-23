from tkinter import *




from tkinter import Tk, Frame, Menu

class Example(Frame):

    def __init__(self):
        super().__init__()

        self.initUI()


    def buildFrames(self):

        self.labelframe = LabelFrame(self.master, text= "Currently Loaded User Mobility Profiles")
        self.labelframe.pack(fill="both", expand="yes")

        left = Label(self.labelframe)
        left.pack()

        labelframe1 = LabelFrame(self.master, text= "Console Log")

        labelframe1.pack(fill="both", expand="yes")
        scrollbary = Scrollbar(self.labelframe)
        scrollbarx = Scrollbar(self.labelframe, orient=HORIZONTAL)

        listbox = Listbox(self.labelframe, yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
        listbox.insert(END, "Riccardo Bertini")
        listbox.insert(END, "Ajeje Brazorf")


        scrollbary.config(command=listbox.yview)
        scrollbarx.config(command=listbox.xview)
        scrollbarx.pack(side=BOTTOM, fill=X)

        listbox.pack(side=LEFT, fill=BOTH)
        scrollbary.pack(side=RIGHT, fill=Y)

        right = Label(self.labelframe)
        right.pack()

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