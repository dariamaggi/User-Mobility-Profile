from tkinter import *




from tkinter import Tk, Frame, Menu

class Example(Frame):

    def __init__(self):
        super().__init__()

        self.initUI()
        self.buildFrames()


    def buildFrames(self):

        labelframe = LabelFrame(self.master)
        labelframe.pack(fill="both", expand="yes")

        left = Label(labelframe)
        left.pack()

        labelframe1 = LabelFrame(self.master)
        labelframe1.pack(fill="both", expand="yes")
        right = Label(labelframe)
        right.pack()

    def initUI(self):

        self.master.title("User Mobility Profile")

        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="File", menu=fileMenu)


    def onExit(self):

        self.quit()


def main():

    root = Tk()
    root.geometry("560x560+300+300")
    app = Example()
    root.mainloop()


if __name__ == '__main__':
    main()