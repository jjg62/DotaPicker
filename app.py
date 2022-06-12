import tkinter
from tkinter import *
from tkinter.ttk import *
import numpy as np
import heroes
import main
import _thread

root = Tk()

def train():
    #Get ID
    id = idField.get()

    #Switch frames
    id_entry_frame.forget()
    loading_frame.pack()

    #Start new thread to train
    _thread.start_new_thread(main.train, (id, 15, bar, show_results, try_again))


def show_results():
    # Switch frames to result
    loading_frame.forget()
    results_frame.pack()

def try_again():
    #Switch frames to input
    loading_frame.forget()
    id_entry_frame.pack()

#Create frames
id_entry_frame = Frame(root)
loading_frame = Frame(root)
results_frame = Frame(root)

#ID Entry Frame
titleLabel = Label(id_entry_frame, text="Welcome to DOTA 2 Hero Picker! ")
explainLabel = Label(id_entry_frame, text="Please enter your OpenDota ID and press Train")
idField = Entry(id_entry_frame, width=50)
idField.insert(END, "113241239")
submitButton = Button(id_entry_frame, text="Train", command=train)

titleLabel.grid(row=0, column=0, columnspan=2)
explainLabel.grid(row=1, column=0, columnspan=2)
idField.grid(row=2, column=0)
submitButton.grid(row=2, column=1)


#Loading Frame
loading_label = Label(loading_frame, text="Training, please wait...")
loading_label.grid(row=0)
bar = Progressbar(loading_frame, orient=HORIZONTAL, length=300)
bar.grid(row=1)


#Results Frame
results_subframe = Frame(results_frame)
results_subframe.pack()
top_3_images = [None, None, None]
top_3_labels = [Label(results_subframe), Label(results_subframe), Label(results_subframe)]
for l in top_3_labels: l.grid(row=2, column=top_3_labels.index(l))



def update_results(top_3):
    #Go through top 3 from best to 3rd best
    for i in range(3):
        hero_name = heroes.get_hero_name(top_3[-i])
        hero_portrait_name = hero_name[14:] + "_sb.png"
        try:
            top_3_images[i] = PhotoImage(file="img/" + hero_portrait_name)
        except TclError:
            #For portraits not found, just use Luna
            top_3_images[i] = PhotoImage(file="img/luna_sb.png")

        top_3_labels[i].config(image=top_3_images[i])


#Top of Results frame
team_vector = np.zeros(13)
display_team_vector = tkinter.StringVar()
display_team_vector.set(str(team_vector))
label_team_vector = Label(results_subframe, textvariable=display_team_vector)
label_team_vector.grid(row=1, columnspan=3)

results_title_label = Label(results_subframe, text="Recommended Picks for You:")
results_title_label.grid(row=0, columnspan=3)

explain_input_label = Label(results_subframe, text="Select the current enemy draft using buttons below:")
explain_input_label.grid(row=3, columnspan=3)

#Query Input Menu
attribute_subframes = {"str": Frame(results_frame), "agi": Frame(results_frame), "int": Frame(results_frame)}
attribute_subframes["str"].pack(pady=20)
attribute_subframes["agi"].pack(pady=20)
attribute_subframes["int"].pack(pady=20)

def clear():
    #Set vector back to 0
    global team_vector
    team_vector = np.zeros(13)
    display_team_vector.set(str(team_vector))

    #Re-nable all hero buttons
    for hb in hero_buttons:
        hero_buttons[hb]["state"] = NORMAL

    update_results(main.query(team_vector))


reset_button = Button(results_subframe, text="Clear Picks", command=clear)
reset_button.grid(row=4, columnspan=3)


def update_team_vector(hid):
    global team_vector

    #Add hero's properties to team vector
    team_vector += heroes.get_hero_property_vector(hid)
    display_team_vector.set(str(team_vector))

    #Disable the button as hero has been picked
    hero_buttons[str(hid)]["state"] = DISABLED
    update_results(main.query(team_vector))


hero_portraits = {}
hero_buttons = {}
buttons_in_each_attribute = {"str": 0, "agi": 0, "int": 0} #Track how many buttons have been added to each category
ROW_MAX = 20 #Max buttons on each row

for hero in heroes.heroes:
    hid = hero["id"]
    attr = hero["primary_attr"]

    #Get name of file to load image from
    portrait_name = hero["name"][14:] + "_sb.png"
    try:
        hero_portraits[str(hid)] = PhotoImage(file="img/" + portrait_name)
    except TclError:
        #If image not found, use Luna
        hero_portraits[str(hid)] = PhotoImage(file="img/luna_sb.png")

    #Make a new button which updates the vector with hero's properties
    hero_buttons[str(hid)] = Button(attribute_subframes[attr], command=lambda h=hid:update_team_vector(h), image=hero_portraits[str(hid)])
    hero_buttons[str(hid)].grid(row=(buttons_in_each_attribute[attr]//ROW_MAX)+1, column=(buttons_in_each_attribute[attr]%ROW_MAX))

    buttons_in_each_attribute[attr] += 1


#Launch ID Entry Frame by default
id_entry_frame.pack()
root.mainloop()