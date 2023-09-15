import time
import numpy as np
from functools import reduce
from clock_gui import gui
import string
import constants
from players.default_player import Player as Default_Player
#have to change inheritance for all of these
from players.default_player import Player as p1
from players.default_player import Player as p2
from players.default_player import Player as p3
from players.default_player import Player as p4
from players.default_player import Player as p5
from players.default_player import Player as p6
from players.default_player import Player as p7
from players.default_player import Player as p8
from players.default_player import Player as p9
from players.default_player import Player as p10
from players.default_player import Player as p11
import time
import pickle as pkl
import copy
import argparse

class  clockGame():
    #def __init__(self, args):
    def __init__(self, args):
        self.use_gui = True
        self.rng = np.random.default_rng(int(args.seed))
        self.max_time = constants.timeout
        with open("log_moves.txt", 'w' ) as f:
            f.write("The game.....has started.")
            f.write('\n')
        self.players = []
        self.player_names = []
        self.curr_state = ["Z" for i in range(24)]    #contains the letters at each of the positions : Z means unoccupied, when occupied will be replaced by actual played letter
        self.curr_territory = [3 for i in range(24)]    #contains the player number (0/1/2) at each of the positions : 3 means unoccupied, when occupied will be replaced by actual played number
        self.letter_position = {}   #dict with every entry as [position, owner]
        for i in list(string.ascii_uppercase):
            self.letter_position[i] = [0,0]                    #player number, position (made for easier indexing and access)
        self.scores = [0,0,0]
        self.state_history = []   #(seq_no, time, player, letter, hour)
        self.time_for_move = []
        self.time_move_start = []
        self.time_choose = [0,0,0]
        self.time_move_end = []
        self.is_game_ended = False
        self.satisfied_constraints = [[],[],[]] 
        self.start_time = 0
        self.end_time = 0
        self.timeout = False
        self.player_instances = [None,None,None]
        self.options_letter = [[],[],[]]
        self.player_type = []
        self.clockapp_instance = None
        self.total_time_taken = 0
        self.unsatisfied_constraints = [[],[],[]]
        self.no_of_constraints = constants.number_of_constraints_pp
        self.constraints_after_discarding = None
        self.indicator_gui_auto = 0
        self.constraints_inputted = [False, False, False]  #To see if the user entered constraint choice has been recorded

        shuffled_letters = list(self.rng.choice(list(string.ascii_uppercase)[:24], 24, replace = False))
        self.options_letter = [shuffled_letters[:8],shuffled_letters[8:16],shuffled_letters[16:24]]
        self.constraints = [[],[],[]]
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
        self.initial_constraints = copy.deepcopy(self.constraints)



    def initialise_player(self, player_px, player_number):
        if player_number == 0:
            if player_px == 0:
                self.player_instances[0] = Default_Player(self.rng)
            elif player_px == 1:
                self.player_instances[0] = p1(self.rng)
            elif player_px == 2:
                self.player_instances[0] = p2(self.rng)
            elif player_px == 3:
                self.player_instances[0] = p3(self.rng)
            elif player_px == 4:
                self.player_instances[0] = p4(self.rng)
            elif player_px == 5:
                self.player_instances[0] = p5(self.rng)
            elif player_px == 6:
                self.player_instances[0] = p6(self.rng)
            elif player_px == 7:
                self.player_instances[0] = p7(self.rng)
            elif player_px == 8:
                self.player_instances[0] = p8(self.rng)
            elif player_px == 9:
                self.player_instances[0] = p9(self.rng)
            elif player_px == 10:
                self.player_instances[0] = p10(self.rng)
            elif player_px == 11:
                self.player_instances[0] = p11(self.rng)
            else:
                self.player_instances[0] = None
        elif player_number == 1:
            if player_px == 0:
                self.player_instances[1] = Default_Player(self.rng)
            elif player_px == 1:
                self.player_instances[1] = p1(self.rng)
            elif player_px == 2:
                self.player_instances[1] = p2(self.rng)
            elif player_px == 3:
                self.player_instances[1] = p3(self.rng)
            elif player_px == 4:
                self.player_instances[1] = p4(self.rng)
            elif player_px == 5:
                self.player_instances[1] = p5(self.rng)
            elif player_px == 6:
                self.player_instances[1] = p6(self.rng)
            elif player_px == 7:
                self.player_instances[1] = p7(self.rng)
            elif player_px == 8:
                self.player_instances[1] = p8(self.rng)
            elif player_px == 9:
                self.player_instances[1] = p9(self.rng)
            elif player_px == 10:
                self.player_instances[1] = p10(self.rng)
            elif player_px == 11:
                self.player_instances[1] = p11(self.rng)
            else:
                self.player_instances[1] = None
        elif player_number == 2:
            if player_px == 0:
                self.player_instances[2] = Default_Player(self.rng)
            elif player_px == 1:
                self.player_instances[2] = p1(self.rng)
            elif player_px == 2:
                self.player_instances[2] = p2(self.rng)
            elif player_px == 3:
                self.player_instances[2] = p3(self.rng)
            elif player_px == 4:
                self.player_instances[2] = p4(self.rng)
            elif player_px == 5:
                self.player_instances[2] = p5(self.rng)
            elif player_px == 6:
                self.player_instances[2] = p6(self.rng)
            elif player_px == 7:
                self.player_instances[2] = p7(self.rng)
            elif player_px == 8:
                self.player_instances[2] = p8(self.rng)
            elif player_px == 9:
                self.player_instances[2] = p9(self.rng)
            elif player_px == 10:
                self.player_instances[2] = p10(self.rng)
            elif player_px == 11:
                self.player_instances[2] = p11(self.rng)
            else:
                self.player_instances[2] = None



    def add_to_log(self, player_number, letter, hour):
        time_taken = self.time_move_end[-1] - self.time_move_start[-1]
        self.time_for_move.append(time_taken)
        self.state_history.append([self.counter-1, time_taken ,player_number, letter, hour])
        student_hour = hour%12
        if student_hour == 0:
            student_hour = 12
        with open("log_moves.txt", 'a' ) as f:
            f.write("Move "+ str(self.counter-1) + " : player " + str(player_number+1) + " ,time " + str(time_taken) + "s, "+ letter + " at " + str(student_hour))
            f.write('\n')
        
    
    def score_calculator(self):
        self.scores = [0,0,0]
        if self.use_gui:
            with open("clock_gui.pkl", "rb") as f:
                self.clockapp_instance = pkl.load(f)
        score_value_list = [1,3,6,12]  #points for satisfying constraints on different lengths
        for i in range(3):
            score = 0
            for j in range(len(self.constraints_after_discarding[i])):
                list_of_letters = self.constraints_after_discarding[i][j].split("<")
                constraint_true_indic = True
                for i2 in range(len(list_of_letters)-1):
                    #Also include intermediate score functionality
                    distance_difference = (self.letter_position[list_of_letters[i2+1]][0]%12) - (self.letter_position[list_of_letters[i2]][0]%12)
                    if distance_difference < 0:
                        distance_difference = distance_difference + 12
                    if not (distance_difference <=5 and distance_difference > 0):
                        constraint_true_indic = False
                if constraint_true_indic == False:
                    score = score - 1
                else:
                    self.satisfied_constraints[i].append(self.constraints_after_discarding[i][j])
                    score = score + score_value_list[len(list_of_letters) - 2]
            self.scores[i] = score
        if self.use_gui:
            self.clockapp_instance["scores"] = self.scores
        print("Player 1 has score " + str(self.scores[0]))
        print("Player 2 has score " + str(self.scores[1]))
        print("Player 3 has score " + str(self.scores[2]))
        tie = False
        winner = np.argmax(np.array(self.scores)) + 1
        if self.scores[winner-1] == self.scores[(winner-2)%3] or self.scores[winner-1] == self.scores[(winner)%3]:
            tie = True
        print("Congratulations Player "+str(winner)+" you are the winner!!!")
        unsatisfied_constraints = copy.deepcopy(self.constraints)
        for i_con in range(3):
            for j_con in range(len(self.satisfied_constraints[i_con])):
                unsatisfied_constraints[i_con].remove(self.satisfied_constraints[i_con][j_con])
        self.unsatisfied_constraints = copy.deepcopy(unsatisfied_constraints)
        if self.use_gui:
            self.clockapp_instance["satisfied_constraints"] = self.satisfied_constraints
            self.clockapp_instance["unsatisfied_constraints"] = self.unsatisfied_constraints
            self.clockapp_instance["initial_constraints"] = self.initial_constraints
        total_time_taken_cumulative = [0,0,0]       #time computation for logs
        for i_tim in range(3):
            for j in range(len(self.time_move_start)):
                if j%3==i_tim:
                    total_time_taken_cumulative[i_tim] = total_time_taken_cumulative[i_tim] + self.time_move_end[j] - self.time_move_start[j]
        with open("log_moves.txt", 'a') as f:
            f.write("Player 1 has score " + str(self.scores[0]) + " with satistied constraints " + str(self.satisfied_constraints[0]) + " unsatisfied constraints "+ str(unsatisfied_constraints[0]) + " and initial constraints "+ str(self.initial_constraints[0]))
            f.write('\n')
            f.write("Player 2 has score " + str(self.scores[1]) + " with satistied constraints " + str(self.satisfied_constraints[1]) + " unsatisfied constraints "+ str(unsatisfied_constraints[1]) + " and initial constraints "+ str(self.initial_constraints[1]))
            f.write('\n')
            f.write("Player 3 has score " + str(self.scores[2]) + " with satistied constraints " + str(self.satisfied_constraints[2]) + " unsatisfied constraints "+ str(unsatisfied_constraints[2]) + " and initial constraints "+ str(self.initial_constraints[2]))
            f.write('\n')
            if tie == False:
                f.write("Congratulations Player "+str(winner)+" you are the winner!!!")
                f.write('\n')
            else:
                f.write("No winner here it's a tie. Or maybe you both (or all of you) are the winners!!")
                f.write('\n')
            f.write("Time taken by player 1, 2 and 3 to choose : "+ str(self.time_choose))
            f.write('\n')
            f.write("Total time taken by player 1, 2 and 3 to decide moves : " + str(total_time_taken_cumulative))
            f.write('\n')
        with open("summary_log.txt", 'w') as f:
            f.write("Final result is as follows : ")
            f.write('\n')
            f.write("Scores for players 1, 2 and 3 : "+ str(self.scores))
            f.write('\n')
            f.write("Satisfied constraints for players 1, 2 and 3 : "+ str(self.satisfied_constraints))
            f.write('\n')
            f.write("total time taken to finish the game : " + str(self.time_move_end[-1] - float(self.start_time))+"s")
            f.write('\n')
            f.write("Time taken by player 1, 2 and 3 to choose : "+ str(self.time_choose))
            f.write('\n')
            f.write("Total time taken by player 1, 2 and 3 to decide moves : " + str(total_time_taken_cumulative))
            f.write('\n')
        if self.use_gui:
            self.clockapp_instance["scores"] = self.scores
        if self.use_gui:
            with open("clock_gui.pkl", "wb") as f:
                pkl.dump(self.clockapp_instance, f)
            #print(self.clockapp_instance['game_actions'])
        #self.is_game_ended = True           #This will ensure the program loop does not continue further.
        exit(1)


    def convert_student_hour_to_mine(self, student_hour):
        if student_hour%12 in self.options_hour:
            return student_hour%12
        elif student_hour%12+12 in self.options_hour:
            return student_hour%12 + 12
        else:
            print("Hour chosen has no slots left.")
            #exit(1)  Not exiting for some strange reason



    def auto_play(self, player_number):
        if len(self.state_history) == 0:
            self.start_time = time.time()
        if not self.constraints_inputted[player_number]:
            choose_start = float(time.time())  
            self.constraints[player_number] = self.player_instances[player_number].choose_discard(self.options_letter[player_number],self.constraints[player_number])
            choose_end = float(time.time())
            self.time_choose[player_number] = choose_end - choose_start
            self.constraints_inputted[player_number] = True
        current_territory = [x+1 for x in self.curr_territory]
        start_play = float(time.time())
        hour_student, letter = self.player_instances[player_number].play(self.options_letter[player_number], self.constraints[player_number], self.curr_state, current_territory)
        end_play = float(time.time())
        self.time_move_start.append(start_play)
        self.time_move_end.append(end_play)
        hour = self.convert_student_hour_to_mine(int(hour_student))
        self.clockapp_instance["game_actions"].append([letter, hour])
        self.clockapp_instance["options_hour"].remove(hour)
        self.clockapp_instance["options_letter"][player_number].remove(letter)
        self.options_hour = self.clockapp_instance["options_hour"]
        self.options_letter = self.clockapp_instance["options_letter"]
        self.counter = self.counter+1
        #self.options_letter[player_number].remove(letter)  Not needed as that's how python works. If a = b (lists) any change in b later also reflects in a
        self.curr_state[hour] = letter
        self.curr_territory[hour] = player_number
        self.letter_position[letter] = [hour,player_number]
        print("player " + str(player_number + 1) + " autoplayed letter "+ letter + " at hour "+ str(hour%12 if hour%12!=0 else 12))
        self.add_to_log(player_number, letter, hour)
        



            
    def run_game(self):
        if self.use_gui:# and self.indicator_gui_auto == 0:
            self.counter = 1   #Counts total number of plays till now
            auto_players = []
            with open("clock_gui.pkl", "rb") as f:
                self.clockapp_instance = pkl.load(f)
            self.options_letter = self.clockapp_instance["options_letter"]          #Pass by reference so will not need to update clockapp instance values, just the self. values.
            self.options_hour = self.clockapp_instance["options_hour"]
            #self.satisfied_constraints = self.clockapp_instance["satisfied_constraints"]
            #self.scores = self.clockapp_instance["scores"]
            #self.initial_constraints = self.clockapp_instance["initial_constraints"]
            
            while not self.is_game_ended: 
                time.sleep(0.3)
                with open("clock_gui.pkl", "rb") as f:
                    self.clockapp_instance = pkl.load(f)
                self.options_letter = self.clockapp_instance["options_letter"]
                self.options_hour = self.clockapp_instance["options_hour"]    
                self.constraints_after_discarding = self.clockapp_instance["constraints_after_discarding"]
                
                if self.clockapp_instance["update_indicator"] == 1:    #Game has just started, waiting for first play so need auto players to play on clock.
                    self.initialise_player(int(self.clockapp_instance["player_0"]), 0)
                    self.initialise_player(int(self.clockapp_instance["player_1"]), 1)
                    self.initialise_player(int(self.clockapp_instance["player_2"]), 2)
                    self.player_type.append(int(self.clockapp_instance["player_0"]))
                    self.player_type.append(int(self.clockapp_instance["player_1"]))
                    self.player_type.append(int(self.clockapp_instance["player_2"]))
                    for i in range(len(self.clockapp_instance["player_indic"])):
                        if self.clockapp_instance["player_indic"][i] == "auto" and self.player_type[i]>=0:
                            auto_players.append(i)
                    
                    
                    if [0,1,2]==auto_players:               #In case the game is on complete autoplay it needs to have differnet logic
                        self.indicator_gui_auto = 1
                        break       
                    
                    if 0 in auto_players:
                        player_0 = self.clockapp_instance["player_0"]
                        choose_start = float(time.time())
                        self.constraints[0] = self.player_instances[0].choose_discard(self.options_letter[0],self.constraints[0])
                        choose_end = float(time.time())
                        self.time_choose[0] = choose_end - choose_start     #time for students code to choose the answer
                        self.constraints_inputted[0] = True
                        self.auto_play(0)
                    if 0 in auto_players and 1 in auto_players:
                        player_1 = self.clockapp_instance["player_1"]
                        choose_start = float(time.time())
                        self.constraints[1] = self.player_instances[1].choose_discard(self.options_letter[1],self.constraints[1])
                        choose_end = float(time.time())
                        self.time_choose[1] = choose_end - choose_start
                        self.constraints_inputted[1] = True
                        self.auto_play(1)
                    if 0 in auto_players and 1 in auto_players and 2 in auto_players:
                        player_2 = self.clockapp_instance["player_2"]
                        choose_start = float(time.time())
                        self.constraints[2] = self.player_instances[2].choose_discard(self.options_letter[2],self.constraints[2])
                        choose_end = float(time.time())
                        self.time_choose[2] = choose_end - choose_start
                        self.constraints_inputted[2] = True
                        self.auto_play(2)
                    self.clockapp_instance["constraints"] = self.constraints
                    #self.constraints = self.clockapp_instance["constraints"]
                    self.clockapp_instance["update_indicator"] = 0
                    with open("clock_gui.pkl", "wb") as f:
                        pkl.dump(self.clockapp_instance, f)
                

                if self.clockapp_instance["update_indicator"] == 2:      #1 if only player names have been selected, 2 if any actual clock entries are present to be recorded.
                    #if self.clockapp_instance["is_listbox"]
                    time.sleep(0.3)
                    with open("clock_gui.pkl", "rb") as f:
                        self.clockapp_instance = pkl.load(f)
                    current_player = (self.counter - 1)%3
                    #print(self.constraints)
                    #update current player characteristic
                    self.start_time = time.time()
                    if current_player == 0 and self.clockapp_instance["constraints_choosing_over"] == True:
                        hour = self.clockapp_instance["game_actions"][-1][1]
                        letter = self.clockapp_instance["game_actions"][-1][0]
                        self.counter = self.counter+1
                        self.constraints = self.clockapp_instance["constraints"]
                        #self.options_letter[0].remove(letter)
                        #self.options_hour.remove(hour)
                        self.curr_state[hour] = letter
                        self.curr_territory[hour] = 0
                        self.letter_position[letter] = [hour,0]
                        print("player 1 played letter "+ letter + " at hour "+ str(hour%12 if hour%12!=0 else 12))
                        time_now = time.time()
                        self.time_move_end.append(time_now)
                        self.time_move_start.append(time_now)
                        self.add_to_log(0, letter, hour)
                        if not self.constraints_inputted[0]:
                            self.constraints[0] = self.clockapp_instance["constraints"][0]
                            self.constraints_inputted[0] = True
                            self.time_choose[0] = 0         #Time 0 anywhere means its a custom player
                        #check next few players until you encounter another non auto
                        if 1 in auto_players:
                            if len(self.options_hour) != 0:
                                self.auto_play(1)
                        if 1 in auto_players and 2 in auto_players:
                            if len(self.options_hour) != 0:
                                self.auto_play(2)
                        #print(self.clockapp_instance["game_actions"])

                    elif current_player == 1 and self.clockapp_instance["constraints_choosing_over"] == True:
                        hour = self.clockapp_instance["game_actions"][-1][1]
                        letter = self.clockapp_instance["game_actions"][-1][0]
                        self.counter = self.counter+1
                        self.constraints = self.clockapp_instance["constraints"]
                        #self.options_letter[1].remove(letter)
                        #self.options_hour.remove(hour)
                        self.curr_state[hour] = letter
                        self.curr_territory[hour] = 1
                        self.letter_position[letter] = [hour,1]
                        print("player 2 played letter "+ letter + " at hour "+ str(hour%12 if hour%12!=0 else 12))
                        time_now = time.time()
                        self.time_move_end.append(time_now)
                        self.time_move_start.append(time_now)
                        self.add_to_log(1, letter, hour)
                        if not self.constraints_inputted[1]:
                            self.constraints[1] = self.clockapp_instance["constraints"][1]
                            self.constraints_inputted[1] = True
                            self.time_choose[1] = 0         #Time 0 anywhere means its a custom player
                        time_now = time.time()
                        if 2 in auto_players:
                            if len(self.options_hour) != 0:
                                self.auto_play(2)
                        if 2 in auto_players and 0 in auto_players:
                            if len(self.options_hour) != 0:
                                self.auto_play(0)

                    elif current_player == 2 and self.clockapp_instance["constraints_choosing_over"] == True:
                        hour = self.clockapp_instance["game_actions"][-1][1]
                        letter = self.clockapp_instance["game_actions"][-1][0]
                        self.counter = self.counter+1
                        self.constraints = self.clockapp_instance["constraints"]
                        #self.options_letter[2].remove(letter)
                        #self.options_hour.remove(hour)
                        self.curr_state[hour] = letter
                        self.curr_territory[hour] = 2
                        self.letter_position[letter] = [hour,2]
                        print("player 3 played letter "+ letter + " at hour "+ str(hour%12 if hour%12!=0 else 12))
                        time_now = time.time()
                        self.time_move_end.append(time_now)
                        self.time_move_start.append(time_now)
                        self.add_to_log(2, letter, hour)
                        if not self.constraints_inputted[2]:
                            self.constraints[2] = self.clockapp_instance["constraints"][2]
                            self.constraints_inputted[2] = True
                            self.time_choose[2] = 0         #Time 0 anywhere means its a custom player
                        time_now = time.time()
                        if 0 in auto_players:
                            if len(self.options_hour) != 0:
                                self.auto_play(0)
                        if 1 in auto_players and 0 in auto_players:
                            if len(self.options_hour) != 0:
                                self.auto_play(1)
                    self.constraints = self.clockapp_instance["constraints"]
                    self.constraints_after_discarding = copy.deepcopy(self.constraints)
                    self.clockapp_instance["constraints_after_discarding"] = self.constraints_after_discarding

                    if self.clockapp_instance["constraints_choosing_over"] == False:
                        self.clockapp_instance["constraints_choosing_over"] = True
                    
                    
                    if len(self.options_hour) == 0:                #Implies that game over
                        print("Game over")
                        with open("clock_gui.pkl", "wb") as f:
                            pkl.dump(self.clockapp_instance, f)
                        self.score_calculator()
                        self.clockapp_instance["satisfied_constraints"] = self.satisfied_constraints
                        self.clockapp_instance["scores"] = self.scores
                        self.clockapp_instance["update_indicator"] = 0
                        with open("clock_gui.pkl", "wb") as f:
                            pkl.dump(self.clockapp_instance, f)
                        self.is_game_ended = True

                    #self.clockapp_instance["update_indicator"] = 0
                self.clockapp_instance["update_indicator"] = 0
                with open("clock_gui.pkl", "wb") as f:
                    pkl.dump(self.clockapp_instance, f)
        
        if (self.use_gui and self.indicator_gui_auto == 1) or not self.use_gui:
            if not self.use_gui:        #If this is the no_gui case
                self.initial_constraints = copy.deepcopy(self.constraints)  #since I am going to change constraints very soon
                print("Choose player 1 : 0 for default player, 1/2/3..11 for p1/p2/p3...")
                player_0 = input()
                self.initialise_player(int(player_0), 0)
                self.player_type.append(int(player_0))
                choose_start = float(time.time())
                self.constraints[0] = self.player_instances[0].choose_discard(self.options_letter[0],self.constraints[0])
                choose_end = float(time.time())
                self.time_choose[0] = choose_end - choose_start
                #self.logger.debug("No GUI flag specified")
                print("Choose player 2 : 0 for default player, 1/2/3..11 for p1/p2/p3...")
                player_1 = input()
                self.initialise_player(int(player_1), 1)
                self.player_type.append(int(player_1))
                choose_start = float(time.time())
                self.constraints[1] = self.player_instances[1].choose_discard(self.options_letter[1],self.constraints[1])
                choose_end = float(time.time())
                self.time_choose[1] = choose_end - choose_start
                print("Choose player 3 : 0 for default player, 1/2/3..11 for p1/p2/p3...")
                player_2 = input()
                self.initialise_player(int(player_2), 2)
                self.player_type.append(int(player_2))
                choose_start = float(time.time())
                self.constraints[2] = self.player_instances[2].choose_discard(self.options_letter[2],self.constraints[2])
                choose_end = float(time.time())
                self.time_choose[2] = choose_end - choose_start
                self.options_hour = list(range(24))
            else:   #if this is the gui but complete autoplay case
                self.initial_constraints = copy.deepcopy(self.constraints)
                choose_start = float(time.time())
                self.constraints[0] = self.player_instances[0].choose_discard(self.options_letter[0],self.constraints[0])
                choose_end = float(time.time())
                self.time_choose[0] = choose_end - choose_start
                choose_start = float(time.time())
                self.constraints[1] = self.player_instances[1].choose_discard(self.options_letter[1],self.constraints[1])
                choose_end = float(time.time())
                self.time_choose[1] = choose_end - choose_start
                choose_start = float(time.time())
                self.constraints[2] = self.player_instances[2].choose_discard(self.options_letter[2],self.constraints[2])
                choose_end = float(time.time())
                self.time_choose[2] = choose_end - choose_start
            self.constraints_inputted[0] = True
            self.constraints_inputted[1] = True
            self.constraints_inputted[2] = True


            self.constraints_after_discarding = copy.deepcopy(self.constraints)
            self.start_time = time.time()
            while len(self.options_hour) != 0:    
                self.counter = 1
                
                current_territory = [x+1 for x in self.curr_territory]
                start_play = float(time.time())
                hour, letter = self.player_instances[0].play(self.options_letter[0], self.constraints[0], self.curr_state, current_territory)
                end_play = float(time.time())
                self.time_move_start.append(start_play)
                self.time_move_end.append(end_play)
                hour = self.convert_student_hour_to_mine(int(hour))
                self.counter = self.counter+1
                self.options_letter[0].remove(letter)
                self.options_hour.remove(int(hour))
                self.curr_state[hour] = letter
                self.curr_territory[hour] = 0
                self.letter_position[letter] = [hour,0]
                print("player 1 played letter "+ letter + " at hour "+ str(hour%12))
                if self.use_gui:
                    self.clockapp_instance["game_actions"].append([letter, hour])
                self.add_to_log(0, letter, hour)
                
                
                current_territory = [x+1 for x in self.curr_territory]
                start_play = float(time.time())
                hour, letter = self.player_instances[1].play(self.options_letter[1], self.constraints[1], self.curr_state, current_territory)
                end_play = float(time.time())
                self.time_move_start.append(start_play)
                self.time_move_end.append(end_play)
                hour = self.convert_student_hour_to_mine(int(hour))
                self.counter = self.counter+1
                self.options_letter[1].remove(letter)
                self.options_hour.remove(int(hour))
                self.curr_state[hour] = letter
                self.curr_territory[hour] = 1
                self.letter_position[letter] = [hour,1]
                print("player 2 played letter "+ letter + " at hour "+ str(hour%12))
                if self.use_gui:
                    self.clockapp_instance["game_actions"].append([letter, hour])
                self.add_to_log(1, letter, hour)
                
                
                current_territory = [x+1 for x in self.curr_territory]
                start_play = float(time.time())
                hour, letter = self.player_instances[2].play(self.options_letter[2], self.constraints[2], self.curr_state, current_territory)
                end_play = float(time.time())
                self.time_move_start.append(start_play)
                self.time_move_end.append(end_play)
                hour = self.convert_student_hour_to_mine(int(hour))
                self.counter = self.counter+1
                self.options_letter[2].remove(letter)
                self.options_hour.remove(int(hour))
                self.curr_state[hour] = letter
                self.curr_territory[hour] = 2
                self.letter_position[letter] = [hour,2]
                print("player 3 played letter "+ letter + " at hour "+ str(hour%12))
                if self.use_gui:
                    self.clockapp_instance["game_actions"].append([letter, hour])
                self.add_to_log(2, letter, hour)
                #print(self.clockapp_instance["game_actions"])
                #print("hi")
                self.end_time = time.time()
                if self.end_time - self.start_time > self.max_time: #timekeeping aspect
                    print("Simulation terminated due to excess time taken.")
                    with open("log_moves.txt", 'a' ) as f:
                        f.write("Simulation terminated due to excess time taken.")
                        f.write('\n')
                    self.timeout = True
                    break
            if not self.timeout:    
                print("Game over")
                with open("clock_gui.pkl", "wb") as f:
                    pkl.dump(self.clockapp_instance, f) 
                self.score_calculator()
                if self.use_gui:
                    self.clockapp_instance["satisfied_constraints"] = self.satisfied_constraints
                    self.clockapp_instance["scores"] = self.scores
                    with open("clock_gui.pkl", "wb") as f:
                        pkl.dump(self.clockapp_instance, f) 
                self.is_game_ended = True
                
        

# Main Function Trigger
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--no_gui", "-ng", default = False, help="Disable GUI")
    parser.add_argument("--seed", "-s", default = 5, help="Choose seed number")
    args = parser.parse_args()
    instance_clockgame = clockGame(args)
    instance_clockgame.use_gui = not args.no_gui
    instance_clockgame.run_game()
