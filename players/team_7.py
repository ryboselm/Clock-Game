from tokenize import String
import numpy as np
from typing import Tuple, List
import random
import math
import time
import numpy
import sys
import string

letters = list(string.ascii_uppercase)
#print(sys.getrecursionlimit())
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

    #def choose_discard(self, cards: list[str], constraints: list[str]):
    def choose_discard(self, cards, constraints):
        """Function in which we choose which cards to discard, and it also inititalises the cards dealt to the player at the game beginning

        Args:
            cards(list): A list of letters you have been given at the beginning of the game.
            constraints(list(str)): The total constraints assigned to the given player in the format ["A<B<V","S<D","F<G<A"].

        Returns:
            list[int]: Return the list of constraint cards that you wish to keep. (can look at the default player logic to understand.)
        """
        final_constraints = []

        for i in range(len(constraints)):
            list_of_letters = constraints[i].split("<")
            for j in cards:
                if j in list_of_letters:
                    final_constraints.append(constraints[i])
                    break
        #print(cards)
        #print(final_constraints)
        return final_constraints



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
        #Do we want intermediate scores also available? Confirm pls

        self.level = 0
        self.time = time.process_time()
        #print(self.time)
        global mx
        state_array = np.array(state)
        duplicate_cards = cards.copy()
        duplicate_state =  state.copy()
        duplicate_territory = territory.copy()
        duplicate_constraints = constraints.copy()
        score = self.getCurrentScore(constraints, state_array, territory)
        child, util = self.maximize(duplicate_cards, duplicate_state,
                                    duplicate_territory, duplicate_constraints, -10000, 10000)
        ##print(self.current_score_calculator(constraints, state, territory))
        '''
        letter = self.rng.choice(cards)
        territory_array = np.array(territory)
        available_hours = np.where(territory_array == 4)
        hour = self.rng.choice(available_hours[0])          #because np.where returns a tuple containing the array, not the array itself
        hour = hour%12 if hour%12!=0 else 12
        '''
        #print(cards)
        letter = child[0]
        hour = child[1]
        hour = hour%12 if hour%12!=0 else 12
        #print(letter)

        return hour, letter
    
    
    def minimize(self, cards, state, territory, constraints, alpha, beta):
        self.level = self.level + 1
        #print(self.level)
        curr_time = time.process_time() - self.time
        availableMoves = self.getAvailableMoves(cards, territory)
        territory_array = np.array(territory)
        available_hours = np.where(territory_array == 4)
        available_hours =  np.array(available_hours)
        if len(available_hours[0]) == 0 or curr_time >= 1:
            return [state, territory], self.getCurrentScore(constraints, cards, territory)
        
        availableLetters = list(set(letters) - set(state) - set(cards))

        minChild, minUtil = 0, 10000
        '''
        for i in range(len(territory_array)):
            if state[i] == 'Z':
                for a in availableLetters:
                    state[i] = a #self.rng.choice(availableLetters) 
                    territory[i] = 0 
                    for j in range(len(territory_array)):
                        if state[j] == 'Z':
                            for b in availableLetters:
                                state[j] = b #self.rng.choice(availableLetters) 
                                territory[j] = 2
                                other, util = self.maximize(cards, state, territory, constraints, alpha, beta)
                                
                                util = util + self.getCurrentScore(constraints, cards, territory)

                                if util < minUtil:
                                    minChild , minUtil = ['A', j], util
                                
                                if minUtil <= alpha:
                                    break
                                
                                if minUtil <= beta:
                                    beta = minUtil
                        state[j] = 'Z'
                        territory[j] = 4
            state[i] = 'Z'
            territory[i] = 4
        '''
        for i in range(2):
            for j in range(len(territory_array)):
                if state[j] == 'Z' and self.rng.random()<=(1/float(len(available_hours[0]))):
                    availableLetters = list(set(letters) - set(state) - set(cards))
                    state[j] = 'A' #random letter for now
                    territory[j] = 0 if i == 0 else 2 #HARDCODED. NEEDS TO BE CHANGED TO OTHER PLAYER #

                    other, util = self.maximize(cards, state, territory, constraints, alpha, beta)
                    
                    util = util + self.getCurrentScore(constraints, cards, territory)

                    if util < minUtil:
                        minChild , minUtil = ['A', j], util
                    
                    if minUtil <= alpha:
                        break
                    
                    if minUtil <= beta:
                        beta = minUtil
                    
        return minChild, minUtil
        

    def maximize(self, cards, state, territory, constraints, alpha, beta):
        self.level = self.level + 1
        curr_time = time.process_time() - self.time
        territory_array = np.array(territory)
        available_hours = np.where(territory_array == 4)
        availableMoves = self.getAvailableMoves(cards, territory)
        if availableMoves == {} or curr_time >= 1:
            return [state, territory], self.getCurrentScore(constraints, cards, territory)
        
        maxChild, maxUtil = 0, -10000
        for child in availableMoves:
            currLetter = child
            for currLocation in availableMoves[child]:
                state[currLocation] = currLetter
                territory[currLocation] = 2 #HARDCODED. NEEDS TO BE CHANGED TO CURRENT PLAYER #
                other, util = self.minimize(cards, state, territory, constraints, alpha, beta)  
                util = util + self.getCurrentScore(constraints, state, territory)
                if util > maxUtil:
                    maxChild, maxUtil = [currLetter, currLocation], util
                    
                if maxUtil >= beta:
                    break
                
                if maxUtil >= alpha:
                    alpha = maxUtil
            
        return maxChild, maxUtil

    def getAvailableMoves(self, cards, territory):
        availableMoves = {}
        territory_array = np.array(territory)
        available_hours = np.where(territory_array == 4)
        for i in cards:
            for j in available_hours:
                availableMoves[i] = j
        return availableMoves

        





    def getCurrentScore(self, constraints, state, territory):
        letter_position = {}
        for i in range(len(state)):
            letter_position[state[i]] = i
        score = 0
        score_value_list = [1,3,12,24]  #points for satisfying constraints on different lengths
        for j in range(len(constraints)):
            list_of_letters = constraints[j].split("<")
            constraint_true_indic = True
            for i2 in range(len(list_of_letters)-1):
                #Also include intermediate score functionality
                if list_of_letters[i2+1] in letter_position and list_of_letters[i2] in letter_position:
                    distance_difference = (letter_position[list_of_letters[i2+1]]%12) - (letter_position[list_of_letters[i2]]%12)
                    if distance_difference < 0:
                        distance_difference = distance_difference + 12
                    if not (distance_difference <=5 and distance_difference > 0):
                        constraint_true_indic = False
                else:
                    constraint_true_indic = False
                if constraint_true_indic == False:
                    score = score - 10
                if constraint_true_indic:
                    score = score + score_value_list[len(list_of_letters) - 2]
        return score*10