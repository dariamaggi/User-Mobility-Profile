from tkinter import *

import datetime
from tkinter.messagebox import showinfo


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
    def readFromUMP(self, user_id, field):
        print("TODO")
    def writefromUMP(self):
        print("TODO")



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
        t = Toplevel(self)
        t.wm_title("User Mobility Profile - "+ value)
        t.geometry("5800x560+350+300")
    def addUser(self):

        t = Toplevel(self)
        t.wm_title("Registration Form")
        t.geometry("560x560+350+300")
        
        lbl_result = Label(t, text=" Registration Form", font=('lato', 18),justify=LEFT)
        lbl_result.grid(row=3,column=2, columnspan=3)

        lbl_name = Label(t, text="Name:",font=('lato', 18), bd=18 , justify=LEFT)
        lbl_name.grid(sticky = W,row=4, column=1)

        name = Entry(t, font=('lato', 18), width=10)
        name.grid(row=4, column=2)

        lbl_surname = Label(t, text="Surname:", font=('lato', 18), bd=18,justify=LEFT)
        lbl_surname.grid(sticky = W,row=4, column=3)

        surname = Entry(t, font=('lato', 18), width=10)
        surname.grid(row=4, column=4)

        lbl_gender = Label(t, text="Gender:",font=('lato', 18), bd=18,justify=LEFT)
        lbl_gender.grid(sticky = W,row=5, column=1)

        var = IntVar()

        rd = Radiobutton(t, text="Male", font=('lato', 18),padx=5, variable=var, value=1)
        rd.grid(row=5, column=2)
        rd1 = Radiobutton(t, text="Female", font=('lato', 18),padx=5, variable=var, value=1)
        rd1.grid(row=5, column=3)
        rd1 = Radiobutton(t, text="Unspecified", font=('lato', 18), padx=5, variable=var, value=1)
        rd1.grid(row=5, column=4)

        lbl_age= Label(t, text="Age:",font=('lato', 18), bd=18, justify=LEFT)
        lbl_age.grid(sticky = W,row=6, column=1)
        #TODO add integer value
        lbl_country = Label(t, text="Nationality:", font=('lato', 18), bd=18, justify=LEFT)
        lbl_country.grid(sticky = W,row=7, column=1)

        list_of_country = ['United States', 'Afghanistan', 'Albania', 'Algeria', 'American Samoa','Andorra', 'Angola','Anguilla', 'Antarctica', 'Antigua And Barbuda','Argentina','Armenia','Aruba', 'Australia', 'Austria','Azerbaijan','Bahamas','Bahrain', 'Bangladesh', 'Barbados', 'Belarus','Belgium','Belize', 'Benin','Bermuda','Bhutan','Bolivia','Bosnia And Herzegowina','Botswana','Bouvet Island', 'Brazil','Brunei Darussalam','Bulgaria','Burkina Faso','Burundi','Cambodia','Cameroon',
            'Canada', 'Cape Verde', 'Cayman Islands','Central African Rep','Chad', 'Chile','China','Christmas Island','Cocos Islands', 'Colombia', 'Comoros','Congo','Cook Islands', 'Costa Rica', 'Cote D`ivoire', 'Croatia', 'Cuba', 'Cyprus',    'Czech Republic','Denmark', 'Djibouti', 'Dominica','Dominican Republic','East Timor','Ecuador', 'Egypt', 'El Salvador','Equatorial Guinea', 'Eritrea', 'Estonia','Ethiopia','Falkland Islands (Malvinas)', 'Faroe Islands','Fiji', 'Finland','France','French Guiana','French Polynesia', 'French S. Territories', 'Gabon',
             'Gambia',    'Georgia',    'Germany',    'Ghana',    'Gibraltar',    'Greece',    'Greenland',    'Grenada',    'Guadeloupe',    'Guam',    'Guatemala',    'Guinea',    'Guinea-bissau',    'Guyana',    'Haiti',    'Honduras','Hong Kong','Hungary','Iceland','India','Indonesia','Iran','Iraq','Ireland',
             'Israel','Italy','Jamaica','Japan','Jordan','Kazakhstan','Kenya','Kiribati','Korea (North)','Korea (South)', 'Kuwait', 'Kyrgyzstan','Laos','Latvia','Lebanon','Lesotho','Liberia','Libya','Liechtenstein','Lithuania','Luxembourg', 'Macau','Macedonia','Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali','Malta', 'Marshall Islands', 'Martinique','Mauritania','Mauritius','Mayotte','Mexico','Micronesia','Moldova','Monaco', 'Mongolia','Montserrat','Morocco', 'Mozambique', 'Myanmar','Namibia',   'Nauru','Nepal','Netherlands','Netherlands Antilles', 'New Caledonia', 'New Zealand','Nicaragua', 'Niger','Nigeria', 'Niue','Norfolk Island', 'Northern Mariana Islands','Norway','Oman','Pakistan', 'Palau', 'Panama','Papua New Guinea','Paraguay', 'Peru','Philippines','Pitcairn','Poland', 'Portugal','Puerto Rico', 'Qatar','Reunion','Romania', 'Russian Federation', 'Rwanda', 'Saint Kitts And Nevis','Saint Lucia','St Vincent/Grenadines', 'Samoa','San Marino', 'Sao Tome','Saudi Arabia', 'Senegal','Seychelles', 'Sierra Leone','Singapore','Slovakia','Slovenia', 'Solomon Islands', 'Somalia', 'South Africa','Spain','Sri Lanka', 'St. Helena','St.Pierre', 'Sudan','Suriname','Swaziland','Sweden','Switzerland','Syrian Arab Republic','Taiwan','Tajikistan','Tanzania', 'Thailand', 'Togo','Tokelau', 'Tonga','Trinidad And Tobago','Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'Uganda','Ukraine', 'United Arab Emirates','United Kingdom', 'Uruguay', 'Vanuatu', 'Vatican City State','Venezuela','Viet Nam','Virgin Islands (British)','Virgin Islands (U.S.)''Western Sahara','Yemen','Yugoslavia','Zaire','Zambia','Zimbabwe']
                # the variable 'c' mentioned here holds String Value, by default ""
        c = StringVar()
        droplist = OptionMenu(t, c, *list_of_country)
        droplist.grid(row=7, column=2, columnspan=2)
        c.set('Select Country')

        t.mainloop()

'''
        #lbl_username = Label(t, text="Name:", bd=18)
        #lbl_username.grid(row=1, column=1)
        lbl_password = Label(t, text="Surname:", bd=18)
        lbl_password.grid(row=2,column=1)
        var = IntVar()
        lbl_gender= Label(t, text="Gender", bd=18)
        lbl_gender.grid(row=8, column=1)
        rd= Radiobutton(t, text="Male", padx=5, variable=var, value=1)
        rd.grid(row=8, column=2)
        rd1 = Radiobutton(t, text="Female", padx=5, variable=var, value=1)
        rd1.grid(row=8, column=3)
        lbl_firstname = Label(t, text="Gender:", font=('arial', 18), bd=18)
        lbl_firstname.grid(row=3,column=1)
        lbl_lastname = Label(t, text="Address:", font=('arial', 18), bd=18)
        lbl_lastname.grid(row=4,column=1)
        lbl_result = Label(t, text=" Registration Form", font=('lato', 18))
        lbl_result.grid(row=1,column=1, columnspan=4)



       # user = Entry(t, font=('lato', 20), width=15)
      #  user.grid(row=1, column=2)
        pass1 = Entry(t, font=('lato', 20),  width=15, show="*")
        pass1.grid(row=2, column=2)
        name = Entry(t, font=('lato', 20), width=15)
        name.grid(row=3, column=2)
        address = Entry(t, font=('lato', 20), width=15)
        address.grid(row=4, column=2)


        btn_register = Button(t, font=('lato', 20), text="Register")
        btn_register.grid(row=6, column=2, columnspan=2)

        # this will run the mainloop.
        t.mainloop()
'''
def main():

    root = Tk()
    root.geometry("560x560+300+300")
    app = MainWindow()
    root.mainloop()


if __name__ == '__main__':
    main()