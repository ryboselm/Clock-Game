from tokenize import String
import numpy as np
from typing import Tuple, List

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
        self.discardPile = []
        self.lettersNeeded = []
        self.nextPlay = None 
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

        for constraint in constraints: 
        #check every constraint to make sure we have atleast 1 letter in every pair in constraint
            if self.__checkPairs(cards, constraint): 
                final_constraints.append(constraint)

        self.__organizeCards(cards, final_constraints)
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
        letter = None 
        for constraint in constraints: 
            if self.__haveAllLetters(cards, constraint): 
                letter = constraint[0]
                self.nextPlay = constraint[2]
        if letter is None and self.nextPlay is not None: 
            letter = self.nextPlay
            self.nextPlay = None
        elif letter is None:
            letter = self.rng.choice(cards)
        territory_array = np.array(territory)
        available_hours = np.where(territory_array == 4)
        hour = self.rng.choice(available_hours[0])          #because np.where returns a tuple containing the array, not the array itself
        hour = hour%12 if hour%12!=0 else 12
        return hour, letter
    
    def __checkPairs(self, cards, constraint): 
    #treat constraint as collection of pairs and check each pair 
        i = 0
        while i < len(constraint)-1:  
            if not self.__havePair(cards, constraint[i], constraint[i+2]):
                return False
            i += 2
        return True

    def __havePair(self, cards, letter1, letter2): 
    #check if we have atleast 1 letter in pair of letters 
        return letter1 in cards or letter2 in cards
    
    def __organizeCards(self, cards, constraints):
        for constraint in constraints: 
            i = 0
            while i < len(constraint): 
                if constraint[i] not in cards and constraint[i] not in self.lettersNeeded: 
                    self.lettersNeeded.append(constraint[i])
                i += 2
        
        for card in cards: 
            if self.__isDiscard(card, constraints): 
                self.discardPile.append(card)

    def __isDiscard(self, card, constraints): 
        for constraint in constraints: 
            if card in constraint: return False 
        return True 

    def __haveAllLetters(self, cards, constraint): 
        i = 0 
        while i < len(constraint):  
            if constraint[i] not in cards: 
                return False
            i+=2
        return True


