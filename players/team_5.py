from tokenize import String
import numpy as np
from typing import Tuple, List
import heapq
import time

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

        self.MAX_CONSTRAINTS = 15 #parameter for the maximum number of constraints we will choose to take.
        self.MAX_CONSTRAINT_SEARCH = 500 #don't look at more than 500 constraints total
        self.CHOOSE_PENALTIES = [0.43, 0.17, 0.95] #heuristic value for likelihood if both adjacent cards are missing from your hand, if one is missing, and if both are present, respectively

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
        num_constraints = min(self.MAX_CONSTRAINT_SEARCH, len(constraints)) #artifically limit the number of constraints seen to 500, seeing more causes problems for some reason


        for constraint in constraints[0:num_constraints]:
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
    
    #Checks whether two constraints directly contradict one another or not. Returns True if there is a contradiction.
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
    
    #returns an expected value for how good a constraint is at the start of game
    def eval_constraint(self, constraint, hand): #returns a number denoting the value of this constraint
        penalty00 = self.CHOOSE_PENALTIES[0] #penalty if two adjacent cards are missing from your hand
        penalty010 = self.CHOOSE_PENALTIES[1] #penalty if two cards are missing around a card you own like 010
        penalty01 = self.CHOOSE_PENALTIES[2] #penalty if you have your card adjacent to a missing card (but it's not the 010 case)
        arr = constraint.split('<')
        n = len(arr)
        scores = [1,3,6,12]
        win_val = scores[len(arr)-2] #the value you get if you win
        con_score = 1.0 #a "constraint score" giving an approximate idea of how likely you are to get it
        for i in range(1, n):
            if i < n-1 and arr[i] in hand and arr[i-1] not in hand and arr[i+1] not in hand:
                con_score*=penalty010
            elif arr[i] not in hand and arr[i-1] not in hand:
                con_score*=penalty00
            elif arr[i] in hand and arr[i-1] in hand:
                pass #do not need to penalize this, a sure thing!
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
        #processes state into a 12x2 list since that's what we coded for originally
        new_state = []
        for i in range(12):
            new_state.append([state[i],state[i+12]])
        state = new_state
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
        # tries every (letter, slot) combo

        #get all open slots right now
        open_slots = []
        where = {}
        for i in range(len(state)):
            for j in state[i]:
                if j == 'Z':
                    open_slots.append(i)
                else:
                    where[j] = i


        #prune consts (constraints) however we can
        #1)
        #consts_subset = self.rng.choice(consts, size=min(len(consts), 5)) #take a RANDOM 5 constraints to look at when calculating the EV since it's too damn slow
        
        #2)
        consts_subset = consts

        #3) discards the constraints that don't have something in hand relevant right now. May do nothing since all would probably have something relevant
        # consts_subset = []
        # for const in consts:
        #     arr = const.split("<")
        #     keep = False
        #     for letter in arr:
        #         if letter in hand:
        #             keep = True
        #             break
        #     if keep:
        #         consts_subset.append(const)
    

        highest_ev = -100000
        highest_move = ('','')
        temp_hand = hand.copy()
        for letter in hand: #up to 8 choices
            for slot in set(open_slots): #up to 12 choices
                #can we do fast invalidation of a choice?
                #if it does not satisfy any subconstraint?


                if state[slot][0] == 'Z':
                    state[slot][0] = letter
                else:
                    state[slot][1] = letter

                temp_hand.remove(letter)
                open_slots.remove(slot)
                where[letter] = slot
                move_ev = self.calc_ev(state, consts_subset, temp_hand, where, open_slots, letter)
                del where[letter]
                temp_hand.append(letter)
                open_slots.append(slot)
                if state[slot][0] == letter:
                    state[slot][0] = 'Z'
                else:
                    state[slot][1] = 'Z'

                if move_ev > highest_ev:
                    highest_ev = move_ev
                    highest_move = (slot, letter)
        print("highest ev move", highest_ev, highest_move)
        return highest_move

    def calc_ev(self, state, consts, hand, where, open_slots, played_letter):
        total_ev = 0
        points = [1, 3, 6, 12]
        for const in consts:
            cc = self.conv_const(state, const, hand)

            #did we violate this constraint by making this play?

            # check if all letters are on the board
            if '1' not in cc[1] and '0' not in cc[1]:
                failed = False
                for i in range(len(cc[0])-1):
                    dist_diff = (where[cc[0][i+1]] - where[cc[0][i]])%12
                    if not (dist_diff <= 5 and dist_diff != 0):
                        failed = True
                if not failed:
                    total_ev += points[len(cc[1]) - 2]
                else:
                    total_ev -= 1
                continue

            #checks each subconstraint individually to see if already violated
            failed = False
            for i in range(len(cc[0])-1):
                if cc[1][i] == '2' and cc[1][i+1] == '2':
                    dist_diff = (where[cc[0][i+1]] - where[cc[0][i]])%12
                    if not (dist_diff <=5 and dist_diff != 0): #at least one of the constraints was invalid
                        total_ev -=1
                        failed = True
                        break
            if failed:
                continue
            

            #no constraint should be already violated past this point!


            #another fastpath
            if played_letter not in cc[0]:
                continue
            #in theory the EV should not have been affected by this change too much

            num_open_slots = len(open_slots)
            num_letters_needed = len(cc[1]) - cc[1].count("2") #number of unsatisfied positions
            ways_to_fill = 1
            for i in range(num_letters_needed): #e.g. 10 open slots, need to put 2 letters down => 10*9
                ways_to_fill*=num_open_slots
                num_open_slots-=1

            successes = self.count_successes(state, cc, where, open_slots) #call into recursive function, runs very slow :(

            p_satisfy = max(successes / ways_to_fill, 1) #in case count_successes breaks and returns something crazy
            #print(successes/ways_to_fill)
            ev = p_satisfy*points[len(cc[1]) - 2] - (1-p_satisfy)
            total_ev += ev
        return total_ev

    #def play(self, cards: list[str], constraints: list[str], state: list[str], territory: list[int]) -> Tuple[int, str]:
    #getAvailSpots: leftpos, rightpos: 0-11 or -1. If leftpos or rightpos are -1 it disregards that side
    #returns it in the full 24 long list ordering. Leftpos means the position 
    def getAvailSpots(self, leftpos, rightpos, open_slots):
        available_hours = set(open_slots)
        if leftpos != -1:
            totheleft = self.five_indices(leftpos, False)
            available_hours = available_hours.intersection(totheleft)
        if rightpos != -1:
            totheright = self.five_indices(rightpos, True)
            available_hours = available_hours.intersection(totheright)
        return available_hours
            
    #helper function
    def five_indices(self, j, before): #j a clock position 0-11 (0 is 12), before Boolean for the 5 before (True) or 5 after (False).
        checklist = set()
        if not before:
            for i in range(j+1,j+6):
                checklist.add(i%12)
        else:
            for i in range(j - 5, j):
                checklist.add(i % 12)
        return checklist


    def count_successes(self, state, conv_const, where, open_slots):
        total_successes = 0

        #if the constraint is already filled
        if '1' not in conv_const[1] and '0' not in conv_const[1]:
            #check if all constraints are satisfied
            for i in range(len(conv_const[0]) - 1):
                dist_diff = (where[conv_const[0][i+1]] - where[conv_const[0][i]])%12
                if not (dist_diff <= 5 and dist_diff != 0):
                    return 0
            return 1


        for i in range(len(conv_const[0])): #loops until it finds the first non-filled constraint
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
                    #fill in state
                    if state[slot][0] == 'Z':
                        state[slot][0] = letter
                    else:
                        state[slot][1] = letter
                    open_slots.remove(slot)
                    where[letter] = slot
                    const_as_list = list(conv_const[1])
                    const_as_list[i] = '2'
                    temp_conv_const = (conv_const[0],''.join(const_as_list)) #new converted constraint

                    successes = self.count_successes(state, temp_conv_const, where, open_slots)

                    open_slots.append(slot) #puts slot back
                    del where[letter]
                    total_successes += successes
                    #empty state again
                    if state[slot][0] == letter:
                        state[slot][0] = 'Z'
                    else:
                        state[slot][1] = 'Z'
                #return after iterating over all valid placements of this letter
                return total_successes

        return total_successes #technically this shouldn't be reachable