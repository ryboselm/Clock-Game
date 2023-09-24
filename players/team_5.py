from tokenize import String
import numpy as np
from typing import Tuple, List
import heapq

class Player:


    def __init__(self, rng: np.random.Generator) -> None:
        """Initialise the player with given skill.

        Args:
            skill (int): skill of your player
            rng (np.random.Generator): numpy random number generator, use this for same player behvior across run
            logger (logging.Logger): logger use this like logger.info("message")
            golf_map (sympy.Polygon): Golf Map polygon
            start (sympy.geometry.Point2D): Start location
            target (sympy.geometry.Point2D): Target location
            map_path (str): File path to map
            precomp_dir (str): Directory path to store/load precomputation
        """
        self.rng = rng
        ### Player Parameters

        self.EV_CUTOFF = 0.85 #Expected Value cutoff parameter
        self.MAX_CONSTRAINTS = 8 #parameter for the maximum number of constraints we will choose to take.
        self.CHOOSE_PENALTIES = [0.3, 0.6, 0.95] #heuristic value for likelihood if both adjacent cards are missing from your hand, if one is missing, and if both are present, respectively

    #def choose_discard(self, cards: list[str], constraints: list[str]):
    def choose_discard(self, cards, constraints):
        """Function in which we choose which cards to discard, and it also inititalises the cards dealt to the player at the game beginning

        Args:
            cards(list): A list of letters you have been given at the beginning of the game.
            constraints(list(str)): The total constraints assigned to the given player in the format ["A<B<V","S<D","F<G<A"].

        Returns:
            list[int]: Return the list of constraint cards that you wish to keep. (can look at the default player logic to understand.)
        """
        maxConstraints = self.MAX_CONSTRAINTS 
        tentative_constraints = [] #maintains value and constraint

        for constraint in constraints:
            value = self.eval_constraint(constraint, cards) #value of a given constraint according to our heuristic
            contradictions = []
            total_contradiction_val = 0
            for tent_constr in tentative_constraints:
                if self.contradicting_constraints(constraint, tent_constr[1]):
                    contradictions.append(tent_constr)
                    total_contradiction_val += tent_constr[0]

            #only add to constraints if the total value of constraints it contradicts is exceeded
            #old conditional: if len(contradictions)==0 and value>0 or len(contradictions)>0 and value >= total_contradiction_val/len(contradictions):
            if value > total_contradiction_val:
                for contradiction in contradictions:
                    tentative_constraints.remove(contradiction)
                if len(contradictions)>0:
                    heapq.heapify(tentative_constraints)
                heapq.heappush(tentative_constraints, (value, constraint))
                #print("push", value, constraint)
            

            #pops the lowest value constraint out to maintain maximum number of constraints.
            if (len(tentative_constraints) > maxConstraints):
                heapq.heappop(tentative_constraints)

        final_constraints = [constr[1] for constr in tentative_constraints]
        print("hand", cards)
        print("final constraints:", tentative_constraints)
        print(" ")
        return final_constraints
    
    #Checks whether two constraints contradict one another or not. Returns True if there is a contradiction.
    def contradicting_constraints(self, con1, con2):
        arr1 = con1.split('<')
        arr2 = con2.split('<')
        for i in range(len(arr1)-1):
            let1 = arr1[i]
            let2 = arr1[i+1]
            for j in range(len(arr2)-1):
                if arr2[j] == let2 and arr2[j+1] == let1: #e.g. say you have A<B<C and C<B. Would return True because of B<C and C<B
                    return True
        return False
    
    #returns a number between 0 and 1 for how good a constraint is at the start of game
    def eval_constraint(self, constraint, hand): #returns a number denoting the value of this constraint
        penalty00 = self.CHOOSE_PENALTIES[0] #penalty if both adjacent cards are missing from your hand
        penalty01 = self.CHOOSE_PENALTIES[1] #penalty if one adjacent card is missing from your hand
        penalty11 = self.CHOOSE_PENALTIES[2] #penalty if both cards are present in your hand
        arr = constraint.split('<')
        scores = [1,3,6,12]
        win_val = scores[len(arr)-2] #the value you get if you win
        con_score = 1.0
        for i in range(len(arr)-1):
            if arr[i] in hand and arr[i+1] in hand:
                con_score*=penalty11
            elif arr[i] not in hand and arr[i+1] not in hand:
                con_score*=penalty00
            else:
                con_score*=penalty01
        return con_score * win_val + (1-con_score) * (-1)

    def conv_const(self, state, con, hand):
        """
        converts a constraint into a tuple of strings: (letters, state)
        0 = in other hand
        1 = in our hand
        2 = on the board
        """
        played = set()
        for hour in state:
            for slot in hour:
                if slot != '':
                    played.add(slot)
        split_con = con.split("<")
        num = ""
        lets = ""
        for i in split_con:
            if i in hand:
                lets += i
                num += '1'
            elif i in played:
                lets += i
                num += '2'
            else:
                lets += i
                num += '0'
        return (lets, num)

    #def play(self, cards: list[str], constraints: list[str], state: list[str], territory: list[int]) -> Tuple[int, str]:
    def play(self, cards, constraints, state, territory):
        """Function which based n current game state returns the distance and angle, the shot must be played

        Args:
            score (int): Your total score including current turn
            cards (list): A list of letters you have been given at the beginning of the game
            state (list(list)): The current letters at every hour of the 24 hour clock
            territory (list(int)): The current occupiers of every slot in the 24 hour clock. 1,2,3 for players 1,2 and 3. 4 if position unoccupied.
            constraints(list(str)): The constraints assigned to the given player

        Returns:
            Tuple[int, str]: Return a tuple of slot from 1-12 and letter to be played at that slot
        """
        move = self.get_highest_move(state, constraints, cards)
        if move == ('', ''):
            print("An error with move selection occurred, playing randomly")
            letter = self.rng.choice(cards)
            territory_array = np.array(territory)
            available_hours = np.where(territory_array == 4)
            hour = self.rng.choice(available_hours[0])
            hour = hour%12 if hour%12!=0 else 12
            return hour, letter
        else:
            return move

    def get_highest_move(self, state, consts, hand):
        # takes in converted constraint
        # pick letter to try
        open_slots = []
        where = {}
        for i in range(len(state)):
            for j in state[i]:
                if j == 'Z':
                    open_slots.append(i)
                else:
                    where[j] = i

        highest_ev = -100000
        highest_move = ('','')
        for letter in hand:
            for slot in set(open_slots):
                if state[slot][0] == 'Z':
                    state[slot][0] = letter
                else:
                    state[slot][1] = letter
                temp_hand = hand.copy()
                temp_hand.remove(letter)
                temp_open_slots = open_slots.copy()
                temp_open_slots.remove(slot)
                where[letter] = slot
                move_ev = self.calc_ev(state, consts, temp_hand, where, temp_open_slots)
                del where[letter]
                if state[slot][0] == letter:
                    state[slot][0] = 'Z'
                else:
                    state[slot][1] = 'Z'

                if move_ev > highest_ev:
                    highest_ev = move_ev
                    highest_move = (slot, letter)

        return highest_move

    def calc_ev(self, state, consts, hand, where, open_slots):
        total_ev = 0
        points = [1, 3, 6, 12]
        for const in consts:
            cc = self.conv_const(state, const, hand)

            # check if all letters are on the board
            if '1' not in cc[1] and '0' not in cc[1]:
                failed = False
                for i in range(len(cc[0] - 1)):
                    
                    if dist_diff < 0:
                        dist_diff *= -1
                    if not (dist_diff <= 5 and dist_diff != 0):
                        failed = True
                if not failed:
                    total_ev += points[len(cc[1]) - 2]
                else:
                    total_ev -= 1
                continue

            #checks each subconstraint individually to see if already violated
            for i in range(len(cc[0])-1):
                if cc[1][i] == '2' and cc[1][i+1] == '2':
                    dist_diff = where[cc[0][i]] - where[cc[0][i + 1]]
                    if dist_diff < 0:
                        dist_diff*= -1
                    if not (dist_diff <=5 and dist_diff != 0): #at least one of the constraints was invalid
                        total_ev -=1
                        continue
            
            #no constraint should be already violated past this point!

            num_open_slots = len(open_slots)
            num_letters_needed = len(cc[1]) - cc[1].count("2") #number of unsatisfied positions
            ways_to_fill = 1
            for i in range(num_letters_needed): #e.g. 10 open slots, need to put 2 letters down => 10*9
                ways_to_fill*=num_open_slots
                num_open_slots-=1

            successes = self.count_successes(state, cc, where, open_slots) #call into recursive function
            p_satisfy = successes / ways_to_fill
            ev = p_satisfy*points[len(cc[1]) - 2] - (1-p_satisfy)
            total_ev += ev
        
        return total_ev

    #def play(self, cards: list[str], constraints: list[str], state: list[str], territory: list[int]) -> Tuple[int, str]:
    #getAvailSpots: leftpos, rightpos: 0-11 or -1. If leftpos or rightpos are -1 it disregards that side
    #returns it in the full 24 long list ordering. Leftpos means the position 
    def getAvailSpots(self, leftpos, rightpos, open_slots):
        available_hours = set(open_slots)
        if leftpos != -1:
            totheleft = self.five_indices(leftpos+1, False)
            available_hours = available_hours.intersection(totheleft)
        if rightpos != -1:
            totheright = self.five_indices(rightpos+1, True)
            available_hours = available_hours.intersection(totheright)
        return available_hours
            
    #helper function
    def five_indices(self, j, before): #j a clock position 0-11 (0 is 12), before Boolean for the 5 before (True) or 5 after (False).
        checklist = set()
        if not before:
            for i in range(j,j+5):
                checklist.add(i%12)
        else:
            for i in range(j - 6, j-1):
                checklist.add(i % 12)
        return checklist


    def count_successes(self, state, conv_const, where, open_slots):
        total_successes = 0

        if '1' not in conv_const[1] and '0' not in conv_const[1]:
            for i in range(len(conv_const[0] - 1)):
                dist_diff = where[conv_const[0][i]] - where[conv_const[0][i + 1]]
                if dist_diff < 0:
                    dist_diff += 12
                if not (dist_diff <= 5 and dist_diff != 0):
                    return 0
            return 1


        for i in range(len(conv_const)):
            letter = conv_const[0][i]
            if conv_const[1][i] != "2":
                right_pos = -1
                left_pos = -1
                if i != 0:
                    if conv_const[1][i-1] == '2':
                        left_pos = where[conv_const[0][i-1]]
                if i != len(conv_const[1])-1:
                    if conv_const[1][i+1] == '2':
                        right_pos = where[conv_const[0][i+1]]
                valid_slots = self.getAvailSpots(left_pos, right_pos, open_slots)
                if len(valid_slots) == 0:
                    return 0
                for slot in valid_slots:
                    if state[slot][0] == 'Z':
                        state[slot][0] = letter
                    else:
                        state[slot][1] = letter
                    temp_open_slots = open_slots.copy()
                    temp_open_slots.remove(slot)
                    where[letter] = slot
                    const_as_list = list(conv_const[1])
                    const_as_list[i] = '2'
                    temp_conv_const = (conv_const[0],''.join(const_as_list))
                    successes = self.count_successes(state, temp_conv_const, where, temp_open_slots)
                    total_successes += open_slots.count(slot) * successes
                    del where[letter]
                    if state[slot][0] == letter:
                        state[slot][0] = 'Z'
                    else:
                        state[slot][1] = 'Z'
                return total_successes
