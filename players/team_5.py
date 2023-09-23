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

    def pick_slot(self, state, const, hand, territory):
        # takes in converted constraint
        # returns best (position,letter) to try and its "odds" of winning
        highest = -1
        highest_i = 0
        highest_left = ('', '')
        highest_right = ('', '')
        returns = [1,3,6,12]
        win_value = returns[len(const[1])-2] #amount you get if you win this constraint

        if '1' not in const[1]: #constraint is totally out of our control now, basically disregard it and do something more important
            return (('', ''), -1)
        
        open_slots = [] #contains which high level clock positions are open rn.
        where = {} #dict matching played letters to clock positions 0-11

        for i in range(len(state)):
            for j in state[i]:
                if j == 'Z':
                    open_slots.append(i)
                else:
                    where[j] = i

        #goal: get a ranking of the urgency of satisfying each subconstraint
        #determines best "score" where score is a product of the presence on left and right of played cards
        #Issue: doesn't really consider which constraints are no longer feasible to satisfy
        for i in range(len(const[0])):
            if const[1][i] == '1': 
                score = 1
                score_left = ('', '')
                score_right = ('', '')

                #surrounding cards are both present, prioritize via one with fewest number of cards remaining
                #also removes from consideration if the constraint cannot be satisfied
                if i==0 and const[1][i+1]=='2':
                    numSpots = len(self.getAvailSpots(-1, where[const[0][i+1]], territory))
                    if numSpots > 0:
                        score = 100/numSpots
                    else:
                        score = -100
                    score_right = (const[0][i + 1], const[1][i + 1])
                elif i==len(const[0])-1 and const[1][i-1]=='2':
                    numSpots = len(self.getAvailSpots(where[const[0][i-1]], -1, territory))
                    if numSpots > 0:
                        score = 100/numSpots
                    else:
                        score = -100
                    score_left = (const[0][i - 1], const[1][i - 1])
                elif i>0 and i<len(const[0])-1 and const[1][i-1]=='2' and const[1][i+1]=='2':
                    numSpots = len(self.getAvailSpots(where[const[0][i-1]], where[const[0][i+1]], territory))
                    if numSpots > 0:
                        score = 100/numSpots
                    else:
                        score = -100
                    score_left = (const[0][i - 1], const[1][i - 1])
                    score_right = (const[0][i + 1], const[1][i + 1])
                else:
                    if i != 0:
                        score = int(const[1][i - 1]) #0 if in other hand, 1 if in our hand, 2 if on board
                        score_left = (const[0][i - 1], const[1][i - 1])
                    if i != len(const[0]) - 1:
                        score *= int(const[1][i + 1])
                        score_right = (const[0][i + 1], const[1][i + 1])
                #print(const[0][i], score)
                if score > highest:
                    highest = score
                    highest_i = i
                    highest_left = score_left
                    highest_right = score_right
        
        
        left_dep_slots = set()
        right_dep_slots = set()
        
        #const is (letters, state)
        #the letters on the left and right of the best part of the constraint to prioritize
        if highest_left[1] == '2':
            basis = where[const[0][highest_i - 1]]
            for i in range(1, 6):
                if (basis + i) % 12 in open_slots:
                    left_dep_slots.add((basis + i) % 12)
        else:
            left_dep_slots = set(open_slots)

        if highest_right[1] == '2':
            basis = where[const[0][highest_i + 1]]
            for i in range(1, 6):
                if (basis - i) % 12 in open_slots:
                    right_dep_slots.add((basis - i) % 12)
        else:
            right_dep_slots = set(open_slots)

        #the selection of slots that satisfy both surrounding constraints
        valid_slots = right_dep_slots.intersection(left_dep_slots)
        #print(valid_slots) 
        if len(valid_slots) == 0:
            #print(open_slots)
            #print(hand)
            #print(state)
            return ((open_slots[0],const[0][highest_i]), 0) #what?
        else:
            most = 0
            most_i = -1
            odds = 0
            left_slots = len(open_slots) - 1
            for slot in valid_slots:
                l_open = 0
                r_open = 0
                open = 0
                temp_odds = 0
                if highest_left[1] == '1' or highest_left[1] == '0':
                    if highest_right[1] == '1' or highest_right[1] == '0':
                        for i in range(1, 6):
                            if (slot - i) % 12 in open_slots:
                                l_open += open_slots.count((slot - i) % 12)
                            if (slot + i) % 12 in open_slots:
                                r_open += open_slots.count((slot + i) % 12)
                        if highest_left[1] == '0':
                            if highest_right[1] == '0':
                                temp_odds = (l_open / left_slots) * (r_open / left_slots)
                            else:
                                if r_open > 2:
                                    temp_odds = 1 * (l_open / left_slots)
                                else:
                                    temp_odds = (l_open / left_slots) * (1 - (1 / left_slots + 1 / left_slots - 1))
                        else:
                            if highest_right[1] == '0':
                                if l_open > 2:
                                    temp_odds = 1 * (r_open / left_slots)
                                else:
                                    temp_odds = (r_open / left_slots) * (1 - (1 / left_slots + 1 / (left_slots - 1)))
                            else:
                                r_fodds = 0
                                l_fodds = 0
                                r_odds = 0
                                l_odds = 0
                                if r_open > 2:
                                    r_odds = 1
                                else:
                                    r_odds = (1 - (1 / left_slots + 1 / (left_slots - 1)))
                                if l_open > 4:
                                    l_odds = 1
                                else:
                                    l_odds = (1 - (1 / left_slots + 1 / (left_slots - 1) + 1 / (left_slots - 2) + 1 / (
                                                left_slots - 3)))
                                r_fodds = l_odds * r_odds
                                if l_open > 2:
                                    l_odds = 1
                                else:
                                    l_odds = (1 - (1 / left_slots + 1 / (left_slots - 1)))
                                if r_open > 4:
                                    r_odds = 1
                                else:
                                    r_odds = (1 - (1 / left_slots + 1 / (left_slots - 1) + 1 / (left_slots - 2) + 1 / (
                                                left_slots - 3)))
                                l_fodds = l_odds * r_odds
                                temp_odds = max(l_fodds, r_fodds)
                        # dif = r_open-l_open
                        # if dif < 0:
                        #   dif*=-1
                        # open = 2*(r_open+l_open)-3*dif
                    else:
                        for i in range(1, 6):
                            if (slot - i) % 12 in open_slots:
                                open += open_slots.count((slot - i) % 12)
                        if highest_left[1] == '0':
                            temp_odds = open / left_slots
                        else:
                            if open > 2:
                                temp_odds = 1
                            else:
                                temp_odds = 1 - (1 / left_slots + 1 / left_slots - 1)


                else:
                    if highest_right[1] == '1' or highest_right[1] == '0':
                        for i in range(1, 6):
                            if (slot + i) % 12 in open_slots:
                                open += open_slots.count((slot + i) % 12)
                        if highest_right[1] == '0':
                            temp_odds = open / left_slots
                        else:
                            if open > 2:
                                temp_odds = 1
                            else:
                                temp_odds = 1 - (1 / left_slots + 1 / left_slots - 1)
                    else:
                        if slot == 0:
                            return (((12, const[0][highest_i]), 1))
                        return (((slot, const[0][highest_i]), 1))
                    if open > most:
                        most = open
                        odds = temp_odds
                        if slot == 0:
                            most_i = 12
                        else:
                            most_i = slot
            return (((most_i, const[0][highest_i]), odds))


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
        return self.get_highest_move(state, constraints, cards)
    
    #getAvailSpots: leftpos, rightpos: 0-11 or -1. If leftpos or rightpos are -1 it disregards that side
    #returns it in the full 24 long list ordering. Leftpos means the position 
    def getAvailSpots(self, leftpos, rightpos, territory):
        territory_array = np.array(territory)
        available_hours = np.where(territory_array == 4)[0]
        if leftpos != -1:
            totheleft = self.five_indices(leftpos+1, False)
            available_hours = self.intersection(available_hours, totheleft)
        if rightpos != -1:
            totheright = self.five_indices(rightpos+1, True)
            available_hours = self.intersection(available_hours, totheright)
        return available_hours
            
    #helper function
    def five_indices(self, j, before): #j a clock position 1-12, before Boolean for the 5 before (True) or 5 after (False).
        if (before):
            if j>=5:
                checklist = list(range(j-5,j)) + list(range(j+7,j+12))
            else:
                checklist = list(range(7+j,12)) + list(range(j)) + list(range(19+j,24)) + list(range(12, j+12))
        else:
            if j <= 6:
                checklist = list(range(j+1, j+6)) + list(range(j+13,j+18))
            else:
                checklist = list(range(j+1,12)) + list(range(0, j-6)) + list(range(j+13,24)) + list(range(12,j+6))
        return checklist

    #helper function
    def intersection(self, lst1, lst2):
        lst3 = [value for value in lst1 if value in lst2]
        return lst3

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

    def calc_ev(self, state, consts, hand, open_slots, where):
        total_ev = 0
        points = [1, 3, 6, 12]
        for const in consts:
            cc = self.conv_const(state, const, hand)

            # all letters are on the board
            if '1' not in cc[1] and '0' not in cc[1]:
                failed = False
                for i in range(len(cc[0] - 1)):
                    dist_diff = where[cc[0][i]] - where[cc[0][i + 1]]
                    if dist_diff < 0:
                        dist_diff += 12
                    if not (dist_diff <= 5 and dist_diff != 0):
                        failed = True
                if not failed:
                    total_ev += points[len(cc[1]) - 2]
                else:
                    total_ev -= 1
                pass

