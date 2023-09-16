try:
    import Tkinter
except:
    import tkinter as Tkinter
import numpy as np
from tkinter import *
import math	# Required For Coordinates Calculation
import time	# Required For Time Handling
import constants as constants
import pickle as pkl
import string
from functools import reduce
import time
import copy
import argparse

canvas_global = None            #Because I cannot pickle this otherwise and multithreading in tkinter is a huge pain.
image_global = None                #Have made all tkinter objects global
root_global = None
button_global = None
label_global = None
drop_hour_global = None
drop_letter_global = None
player_0_global = None
player_1_global = None
player_2_global = None
listbox_global = None
clicked_letter_global = None
clicked_hour_global = None
player_one_global = None
player_two_global = None
player_three_global = None






class gui():
    def __init__(self, args):
        self.use_gui = True
        self.rng = np.random.default_rng(int(args.seed))
        self.no_of_constraints = constants.number_of_constraints_pp
        
        self.x=250	# Center Point x
        self.y=270	# Center Point
        self.length=205	# Stick Length
        
        self.options_player = ["custom_player","default_player", "p1", "p2", "p3","p4","p5", "p6","p7", "p8", "p9","p10", "p11"]
        self.hours = [[],[],[]]
        self.letters_played = [[],[],[]]
        self.game_actions = []          #records [letter, hour] of every move
        self.list_scores = []
        self.status_indicator = "start"  #can be start or end. Used in show function to show and not show certain items.
        self.player_indic = ["auto", "auto", "auto"] #to keep track of what has been shown for which player and which player should be automated
        
        self.start_time = 0
        self.end_time = 0
        self.max_time = constants.timeout

        self.custom_players = []
        self.show_count = 0 #to keep track of how many players have already played
        self.winner = 4
        self.is_listbox = False
        self.update_indicator = 0
        self.satisfied_constraints = [[],[],[]]
        self.scores = [0,0,0]

        shuffled_letters = list(self.rng.choice(list(string.ascii_uppercase)[:24], 24, replace = False))
        self.options_letter = [shuffled_letters[:8],shuffled_letters[8:16],shuffled_letters[16:24]]
        self.options_hour = list(range(24))
        self.constraints = [[],[],[]]
        self.initial_constraints = [[],[],[]]
        self.unsatisfied_constraints = [[],[],[]]
        self.constraints_after_discarding = [[],[],[]]
        self.player_0 = None
        self.player_1 = None
        self.player_2 = None

        self.constraints_choosing_over = False
        
        for j in range(3):
            constraint_counter = 0
            const_exceeded = False
            while True:
                for i in range(2,6):            
                    constraints_choice = self.rng.choice(list(string.ascii_uppercase)[:24], i, replace = False)     #I am preventing repetition of letters here since it makes some constraints impossible
                    delim = "<"
                    res = reduce(lambda x, y: str(x) + delim + str(y), constraints_choice)
                    constraint_string = str(res)
                    constraint_counter = constraint_counter + 1
                    if constraint_counter <= self.no_of_constraints:
                        self.constraints[j].append(constraint_string)
                    else:
                        const_exceeded = True
                if const_exceeded == True:
                    break

        #self.chosen_hour_indicator = [0,0,0,0,0,0,0,0,0,0,0,0] #for hour dropdown. 0 if hour available from 1-12, 1 if hour available from 13-24, 3 if not available.
        


    def draw_letter(self, letter: str, position: int, player_number):
        global root_global
        global image_global
        global canvas_global
        global button_global
        global label_global
        global drop_letter_global
        global drop_hour_global
        global player_0_global
        global player_1_global
        global player_2_global
        global listbox_global
        global clicked_letter_global
        global clicked_hour_global
        global player_one_global
        global player_two_global
        global player_three_global
        if position >= 12:
            k = 1
        else:
            k=-1
        if player_number == 0:
            canvas_global.create_text(self.x +(self.length + constants.exact_pos + 10*k)*math.cos(math.radians((position%12-3)*30)) ,self.y + (self.length + constants.exact_pos + 10*k)*math.sin(math.radians((position%12-3)*30)),text=letter, fill="black")
        elif player_number == 1:
            canvas_global.create_text(self.x +(self.length + constants.exact_pos + 10*k)*math.cos(math.radians((position%12-3)*30)) ,self.y + (self.length + constants.exact_pos + 10*k)*math.sin(math.radians((position%12-3)*30)),text=letter, fill="blue")
        else:
            canvas_global.create_text(self.x +(self.length + constants.exact_pos + 10*k)*math.cos(math.radians((position%12-3)*30)) ,self.y + (self.length + constants.exact_pos + 10*k)*math.sin(math.radians((position%12-3)*30)),text=letter, fill="red")
        return

    #show cards and constraints
    #show this table
    #have a drop down menu of letters and position to choose from
    def end_run(self):
        exit(1)


    def draw_table(self):
        global root_global
        global image_global
        global canvas_global
        global button_global
        global label_global
        global drop_letter_global
        global drop_hour_global
        global player_0_global
        global player_1_global
        global player_2_global
        global listbox_global
        global clicked_letter_global
        global clicked_hour_global
        global player_one_global
        global player_two_global
        global player_three_global
        self.update_variables()
        root_global = Tkinter.Tk()
        self.winner = np.argmax(np.array(self.scores)) + 1
        player_name = ["","",""]
        player_name[0] = "Default Player" if self.player_0 == 0 else "Team "+str(self.player_0)
        player_name[1] = "Default Player" if self.player_1 == 0 else "Team "+str(self.player_1)
        player_name[2] = "Default Player" if self.player_2 == 0 else "Team "+str(self.player_2)
        for indic_custom in self.custom_players:
            player_name[indic_custom] = "Custom Player"
        
        discarded_constraints = copy.deepcopy(self.initial_constraints)         #Since there is no variable for discarded constraints and initial constraints were too long for the table
        for i_con in range(3):
            for j_con in range(len(self.satisfied_constraints[i_con])):
                discarded_constraints[i_con].remove(self.satisfied_constraints[i_con][j_con])
            for j_con in range(len(self.unsatisfied_constraints[i_con])):
                discarded_constraints[i_con].remove(self.unsatisfied_constraints[i_con][j_con])        
        list_scores = [("Sr.No. ",'Player Number', "Player Name", "Scores", "Satisfied Constraints", "Unsatisfied Constraints", "Discarded Constraints"),
                (1,'Player 1', player_name[0], self.scores[0], ", ".join([str(ele) for ele in self.satisfied_constraints[0]]), ", ".join([str(ele) for ele in self.unsatisfied_constraints[0]]), ", ".join([str(ele) for ele in discarded_constraints[0]])),
                (2,'Player 2', player_name[1], self.scores[1], ", ".join([str(ele) for ele in self.satisfied_constraints[1]]), ", ".join([str(ele) for ele in self.unsatisfied_constraints[1]]), ", ".join([str(ele) for ele in discarded_constraints[1]])),
                (3,'Player 3', player_name[2], self.scores[2], ", ".join([str(ele) for ele in self.satisfied_constraints[2]]), ", ".join([str(ele) for ele in self.unsatisfied_constraints[2]]), ", ".join([str(ele) for ele in discarded_constraints[2]]))]
        for i in range(4):
            for j in range(7):
                self.e = Entry(root_global, width=30, fg='blue',
                               font=('Arial',16,'bold'))
                self.e.grid(row=i, column=j)
                self.e.insert(END, list_scores[i][j])
        button_global = Button( root_global , text = "Exit App" , command = self.end_run )
        button_global.place(x=123, y=20)

    # creating Canvas
    def create_canvas_for_shapes(self):
        global root_global
        global image_global
        global canvas_global
        global button_global
        global label_global
        global drop_letter_global
        global drop_hour_global
        global player_0_global
        global player_1_global
        global player_2_global
        global listbox_global
        global clicked_letter_global
        global clicked_hour_global
        global player_one_global
        global player_two_global
        global player_three_global
        canvas_global=Tkinter.Canvas(root_global, width = 500, height = 550, bg='#E5E6DC')
        canvas_global.pack(expand='yes',fill='both')
        return

    def convert_to_dict(self):
        my_dict = {}
        my_variables = ['use_gui', 'rng', 'no_of_constraints', 'hours', 'letters', 'game_actions', 'list_scores', 'status_indicator', 'player_indic', 'start_time', 'end_time', 'max_time', 'custom_players', 'show_count', 'winner', 'is_listbox', 'update_indicator', 'satisfied_constraints', 'scores', 'options_letter', 'options_hour', 'constraints', 'player_one', 'player_two', 'player_three']
        my_dict['use_gui'] = self.use_gui
        my_dict['rng'] = self.rng
        my_dict['no_of_constraints'] = self.no_of_constraints
        my_dict['hours'] = self.hours
        my_dict['letters_played'] = self.letters_played
        my_dict['game_actions'] = self.game_actions
        my_dict['list_scores'] = self.list_scores
        my_dict['status_indicator'] = self.status_indicator
        my_dict['player_indic'] = self.player_indic
        my_dict['start_time'] = self.start_time
        my_dict['end_time'] = self.end_time
        my_dict['custom_players'] = self.custom_players
        my_dict['show_count'] = self.show_count
        my_dict['update_indicator'] = self.update_indicator
        my_dict['satisfied_constraints'] = self.satisfied_constraints
        my_dict['options_letter'] = self.options_letter
        my_dict['options_hour'] = self.options_hour
        my_dict['constraints'] = self.constraints
        my_dict['player_0'] = self.player_0
        my_dict['player_1'] = self.player_1
        my_dict['player_2'] = self.player_2
        my_dict['scores'] = self.scores
        my_dict['satisfied_constraints'] = self.satisfied_constraints
        my_dict['initial_constraints'] = self.initial_constraints
        my_dict['unsatisfied_constraints'] = self.unsatisfied_constraints
        my_dict['constraints_after_discarding'] = self.constraints_after_discarding
        my_dict['constraints_choosing_over'] = self.constraints_choosing_over

        return(my_dict)

    def update_variables(self):     #Update all the variables that were changed in the backend (clock_game.py)
        with open("clock_gui.pkl", "rb") as f:
            my_dict = pkl.load(f)
        self.use_gui = my_dict['use_gui']
        self.rng = my_dict['rng']
        self.no_of_constraints = my_dict['no_of_constraints']
        self.hours = my_dict['hours']
        self.letters_played = my_dict['letters_played']
        self.game_actions = my_dict['game_actions']
        self.list_scores = my_dict['list_scores']
        self.status_indicator = my_dict['status_indicator']
        self.player_indic = my_dict['player_indic']
        self.start_time = my_dict['start_time']
        self.end_time = my_dict['end_time']
        self.custom_players = my_dict['custom_players']
        self.show_count = my_dict['show_count']
        self.update_indicator = my_dict['update_indicator']
        self.satisfied_constraints = my_dict['satisfied_constraints']
        self.options_letter = my_dict['options_letter']
        self.options_hour = my_dict['options_hour']
        self.constraints = my_dict['constraints']
        self.player_0 = my_dict['player_0']
        self.player_1 = my_dict['player_1']
        self.player_2 = my_dict['player_2']
        self.scores = my_dict['scores']
        self.satisfied_constraints = my_dict['satisfied_constraints']
        self.initial_constraints = my_dict['initial_constraints']
        self.unsatisfied_constraints = my_dict['unsatisfied_constraints']
        self.constraints_after_discarding = my_dict['constraints_after_discarding']
        self.constraints_choosing_over = my_dict['constraints_choosing_over']


    



    
    def start_game(self):
        global root_global
        global image_global
        global canvas_global
        global button_global
        global label_global
        global drop_letter_global
        global drop_hour_global
        global player_0_global
        global player_1_global
        global player_2_global
        global listbox_global
        global clicked_letter_global
        global clicked_hour_global
        global player_one_global
        global player_two_global
        global player_three_global
        self.update_indicator = 1

        if self.status_indicator == "start":
            
            player_0_type = player_0_global.get() #Assigning the types of players 1, 2 and 3
            player_1_type = player_1_global.get()
            player_2_type = player_2_global.get()
            
            self.player_0 = self.options_player.index(player_0_type) - 1        #int of player type from 0-11
            self.player_1 = self.options_player.index(player_1_type) - 1
            self.player_2 = self.options_player.index(player_2_type) - 1

            my_dict = self.convert_to_dict()
            with open("clock_gui.pkl", "wb") as f:
                pkl.dump(my_dict, f)

            time.sleep(0.5)
            self.update_variables()
            #for i_actions in self.game_actions:
                #self.draw_letter(i_actions[0], i_actions[1], self.game_actions.index(i_actions)%3)

            if player_0_type == "custom_player":
                self.player_indic[0] = "start"
                self.custom_players.append(0)
            if player_1_type == "custom_player":
                self.player_indic[1] = "start"
                self.custom_players.append(1)
            if player_2_type == "custom_player":
                self.player_indic[2] = "start"
                self.custom_players.append(2)
            
            if len(self.custom_players) == 0:
                my_dict = self.convert_to_dict()
                with open("clock_gui.pkl", "wb") as f:
                    pkl.dump(my_dict, f)
                button_global.destroy()
                player_one_global.destroy()
                player_two_global.destroy()
                player_three_global.destroy()

                for i_auto in range(24):
                    time.sleep(0.08)
                    label_global.config( text = "Game simulation has run! Click above to see results!")
                self.update_variables()
                for i_actions in self.game_actions:
                    self.draw_letter(i_actions[0], i_actions[1], self.game_actions.index(i_actions)%3)
                button = Button( root_global , text = "See results" , command = self.draw_table )
                button.place(x=123, y=20)

            else:
                if len(self.custom_players) == 1:
                    button_global.destroy()
                    player_one_global.destroy()
                    player_two_global.destroy()
                    player_three_global.destroy()
                    button_global = Button( root_global , text = "Choose last constraint" , command = self.show)
                    button_global.place(x=123, y=20)
                    listbox_global = Listbox(root_global, selectmode = "multiple")
                    # Widget expands horizontally and vertically by assigning as both
                    listbox_global.pack(expand = YES, fill = "both")
                    for each_item in range(len(self.constraints[self.custom_players[0]])):
                        listbox_global.insert(END, self.constraints[self.custom_players[0]][each_item])
                        listbox_global.itemconfig(each_item)
                    self.is_listbox = True
                    self.player_indic[self.custom_players[0]] = "in_progress"
                    label_global.config( text = "It's your chance player "+str(self.custom_players[0]+1)+ " with letters "+str(self.options_letter[self.custom_players[0]]))
                else:
                    button_global.destroy()
                    player_one_global.destroy()
                    player_two_global.destroy()
                    player_three_global.destroy()
                    button_global = Button( root_global , text = "Choose constraints" , command = self.choosing_cards )
                    button_global.place(x=123, y=20)
                    listbox_global = Listbox(root_global, selectmode = "multiple")
                    # Widget expands horizontally and vertically by assigning as both
                    listbox_global.pack(expand = YES, fill = "both")
                    for each_item in range(len(self.constraints[self.custom_players[0]])):
                        listbox_global.insert(END, self.constraints[self.custom_players[0]][each_item])
                        listbox_global.itemconfig(each_item)
                    self.is_listbox = True
                    self.player_indic[self.custom_players[0]] = "in_progress"
                    label_global.config( text = "It's your chance player "+str(self.custom_players[0]+1)+ " with letters "+str(self.options_letter[self.custom_players[0]]))



            my_dict = self.convert_to_dict()
            with open("clock_gui.pkl", "wb") as f:
                pkl.dump(my_dict, f)


    def choosing_cards(self):
        global root_global
        global image_global
        global canvas_global
        global button_global
        global label_global
        global drop_letter_global
        global drop_hour_global
        global player_0_global
        global player_1_global
        global player_2_global
        global listbox_global
        global clicked_letter_global
        global clicked_hour_global
        global player_one_global
        global player_two_global
        global player_three_global
        #Will use self.show_count first only for choosing the chosen cards count
        

        index = (self.show_count % len(self.custom_players))
        if index <0:
            index = index + len(self.custom_players)
        self.show_count = self.show_count + 1
        current_player = self.custom_players[index]

        if player_one_global != None: #or if index == 0 (first constraints being chosen)
            player_one_global.destroy()
            player_two_global.destroy()
            player_three_global.destroy()
        button_global.destroy()
        
        if self.is_listbox:
            self.constraints[current_player] = []
            for i in listbox_global.curselection():
                self.constraints[current_player].append(listbox_global.get(i))
            listbox_global.destroy()
            self.is_listbox = False
            my_dict = self.convert_to_dict()
            with open("clock_gui.pkl", "wb") as f:
                pkl.dump(my_dict, f)

        

        
        next_player = self.custom_players[((self.show_count) % len(self.custom_players))]
        button_global.destroy()
        if next_player != self.custom_players[-1]:
            button_global = Button( root_global , text = "Choose constraints" , command = self.choosing_cards )
            button_global.place(x=123, y=20)
            label_global.config( text = "It's your chance player "+str(next_player+1)+ " with letters "+str(self.options_letter[next_player]))
            #drop_hour_global = OptionMenu( root_global , clicked_hour_global , *self.options_hour )
            self.status_indicator = "in_progress"
            listbox_global = Listbox(root_global, selectmode = "multiple")
            # Widget expands horizontally and vertically by assigning as both
            listbox_global.pack(expand = YES, fill = "both")
            for each_item in range(len(self.constraints[next_player])):
                listbox_global.insert(END, self.constraints[next_player][each_item])
                listbox_global.itemconfig(each_item)
            self.is_listbox = True
            self.player_indic[next_player] = "in_progress"
        else:
            button_global = Button( root_global , text = "Choose last constraint" , command = self.show )
            button_global.place(x=123, y=20)
            label_global.config( text = "It's your chance player "+str(next_player+1)+ " with letters "+str(self.options_letter[next_player]))
            self.status_indicator = "in_progress"
            self.show_count = 0
            listbox_global = Listbox(root_global, selectmode = "multiple")
            listbox_global.pack(expand = YES, fill = "both")
            for each_item in range(len(self.constraints[next_player])):
                listbox_global.insert(END, self.constraints[next_player][each_item])
                listbox_global.itemconfig(each_item)
            self.is_listbox = True
            self.player_indic[next_player] = "in_progress"
            my_dict = self.convert_to_dict()
            with open("clock_gui.pkl", "wb") as f:
                pkl.dump(my_dict, f)


    def show(self):
        global root_global
        global image_global
        global canvas_global
        global button_global
        global label_global
        global drop_letter_global
        global drop_hour_global
        global player_0_global
        global player_1_global
        global player_2_global
        global listbox_global
        global clicked_letter_global
        global clicked_hour_global
        global player_one_global
        global player_two_global
        global player_three_global
        
        
        self.update_indicator = 2
        button_global.destroy()
        my_dict = self.convert_to_dict()
        
        
        
        if self.is_listbox:
            current_player = self.custom_players[-1]%3
            next_player = self.custom_players[0]%3
            self.constraints[current_player] = []
            for i in listbox_global.curselection():
                self.constraints[current_player].append(listbox_global.get(i))
            listbox_global.destroy()
            self.is_listbox = False
            self.show_count = -1

        else:
            current_player = self.custom_players[self.show_count%len(self.custom_players)]
            next_player = self.custom_players[(self.show_count+1)%len(self.custom_players)]
            self.constraints_choosing_over = True
            letter = clicked_letter_global.get()
            hour = int(clicked_hour_global.get())
            if hour%12 in self.options_hour:
                if hour == 12:
                    hour = 0
                else:
                    hour = hour
            elif hour%12 + 12 in self.options_hour:
                if hour == 12:
                    hour = 12
                else:
                    hour = hour + 12 
            self.game_actions.append([letter, int(hour)])
            self.hours[current_player].append(hour)
            self.letters_played[current_player].append(letter)
            self.options_letter[current_player].remove(letter)          #actions for old player
            self.options_hour.remove(int(hour))
            drop_hour_global.destroy()
            drop_letter_global.destroy()
            #Adding the selection to the clock

        self.show_count = self.show_count + 1
        my_dict = self.convert_to_dict()
        with open("clock_gui.pkl", "wb") as f:
            pkl.dump(my_dict, f)
        time.sleep(1.2)
        self.update_variables()
        
        
        
        for i_actions in self.game_actions:
            self.draw_letter(i_actions[0], i_actions[1], self.game_actions.index(i_actions)%3)
        
        
        
        sum_of_custom_letters_left = 0
        for j in self.custom_players:
            sum_of_custom_letters_left = sum_of_custom_letters_left + len(self.options_letter[j])
        if len(self.options_hour) == 0 or sum_of_custom_letters_left == 0:
            #function to get winner of game
            self.status_indicator = "end"
            self.winner = np.argmax(np.array(self.scores)) + 1
            self.update_variables()
            label_global.config( text = "Game Over, click above to see results!!")
            #Display the scores result table here
            button = Button( root_global , text = "See results" , command = self.draw_table )
            button.place(x=123, y=20)
        else:
            constraints_string = str(reduce(lambda x, y: str(x) + ", " + str(y), self.constraints[next_player]))           #to display the constraints for every player
            label_global.config( text = "It's your chance player "+str(next_player+1)+" with constraints "+constraints_string) #+ clicked_letter_global.get() + " at position " + clicked_hour_global.get())
            clicked_letter_global.set( "Choose your letter" )
            clicked_hour_global.set( "Choose your hour" )
            drop_letter_global = OptionMenu( root_global , clicked_letter_global , *self.options_letter[next_player] )
            drop_letter_global.pack()
            display_hour = []
            indicator_12 = 0
            button = Button( root_global , text = "Play" , command = self.show )
            button.place(x=123, y=20)

            for i in range(12):     #To see which positions are available in the clock from 1 to 12. Since in my own data structure it is stored as 0 to 23.
                if i in self.options_hour:
                    #self.chosen_hour_indicator[i] = 0
                    if i!=0:
                        display_hour.append(i)
                    else:
                        indicator_12 = 1
                elif i+12 in self.options_hour:
                    #self.chosen_hour_indicator[i] = 1
                    if i!=0:
                        display_hour.append(i)
                    else:
                        indicator_12 = 1
                #else:
                    #self.chosen_hour_indicator[i] = 3
            if indicator_12 == 1:
                display_hour.append(12)

            drop_hour_global = OptionMenu( root_global , clicked_hour_global , *display_hour )
            drop_hour_global.pack() 
        self.constraints_after_discarding = copy.deepcopy(self.constraints)
        my_dict = self.convert_to_dict()
        with open("clock_gui.pkl", "wb") as f:
            pkl.dump(my_dict, f)

        


    def run(self):  
        global root_global
        global image_global
        global canvas_global  
        global button_global
        global label_global
        global drop_letter_global
        global drop_hour_global
        global player_0_global
        global player_1_global
        global player_2_global
        global listbox_global
        global clicked_letter_global
        global clicked_hour_global
        global player_one_global
        global player_two_global
        global player_three_global
        root_global = Tkinter.Tk()
        #creating the background canva
        canvas_global=Tkinter.Canvas(root_global, width = 500, height = 550, bg='#E5E6DC')
        canvas_global.pack(expand='yes',fill='both')
        image_global=Tkinter.PhotoImage(file='clock.gif')
        canvas_global.create_image(250,270, image=image_global)
        clicked_letter_global = StringVar()
        clicked_letter_global.set( "Choose your letter" )
        # datatype of menu text
        clicked_hour_global = StringVar()
        # initial menu text
        clicked_hour_global.set( "Choose your hour" )
        label_global = Label( root_global , text = " " )
        player_0_global = StringVar()
        player_0_global.set("Choose player 1")
        player_one_global = OptionMenu( root_global , player_0_global , *self.options_player )
        player_one_global.pack()

        player_1_global = StringVar()
        player_1_global.set("Choose player 2")
        player_two_global = OptionMenu( root_global , player_1_global , *self.options_player )
        player_two_global.pack()

        player_2_global = StringVar()
        player_2_global.set("Choose player 3")
        player_three_global = OptionMenu( root_global , player_2_global , *self.options_player )
        player_three_global.pack()

        # Create Label
        label_global.pack()

        # Create button, it will change label text
        button_global = Button( root_global , text = "Start Game" , command = self.start_game )
        button_global.place(x=123, y=20)

        listbox_global = Listbox(root_global, selectmode = "multiple")

        root_global.mainloop()
    





# Main Function Trigger
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", "-s", default = 5, help="Choose seed number")
    args = parser.parse_args()
    instance = gui(args)
    my_dict = instance.convert_to_dict()
    with open("clock_gui.pkl", "wb") as f:
        pkl.dump(my_dict, f)
    instance.run()