from tokenize import String
import numpy as np
from typing import Tuple, List
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
        stripped_constraints = []
        # print("CONSTRAINTS")
        # print(constraints)

        # print("CARDS")
        # print(cards)

        for i in range(len(constraints)):
            # splits current constraint into array of letters and removes <'s 
            curr = constraints[i].split('<')
            while '<' in curr:
                curr.remove('<')
            numLetters = len(curr)
            
            # see how many letters in a constraint we have 
            matches = 0
            for letter in curr:
                if letter in cards:
                    matches += 1

            match numLetters:
                    case 2:
                        if(matches == 1) or (matches == 2):
                            final_constraints.append(constraints[i])
                    case 3:
                        if(matches == 2):
                            final_constraints.append(constraints[i])
                    case 4:
                        if(matches == 3):
                            final_constraints.append(constraints[i])
                        elif((curr[0] in cards and curr[2] in cards) or (curr[1] in cards and curr[3] in cards)):
                            final_constraints.append(constraints[i])
                    case 5:
                        if(matches == 4):
                            final_constraints.append(constraints[i])
                        elif((curr[0] in cards and curr[2] in cards and curr[4] in cards)):
                            final_constraints.append(constraints[i]) 

            # if we don't have any letters in a constraint don't choose it 

            #if(len(final_constraints) == 0){
            #}
  
            #if self.rng.random()<=0.5:
            #   final_constraints.append(constraints[i])

        # print("FINAL")
        # print(final_constraints)
        return final_constraints

    def is_played(self, letter, state):
        for i in range(len(state)):
            if letter in state[i]:
                return (True, i)
        return (False, -1)
    
    # def bestMove (self, available_hours, cards):
    #     bestScore = float('-inf')
    #     moves = [[]]
    #     bestMove = []
    #     for i in available_hours:
    #         for x in cards:
    #             hour = i
    #             letter = x
    #             score = self.minimax(clock, hour, letter, 0, true)
    #             if (score>bestScore):
    #                 bestScore = score
    #                 bestMove = [i,x]
        
    #     return bestMove

        
    def getAvailableMoves(self, cards, state):
        availableMoves = {}
        state_array = np.array(state)
        available_hours = np.where(state_array == 'Z')
        for i in available_hours:
            for x in cards:
                availableMoves.append(i,x)
        return availableMoves
    

    # function to get unplayed cards on the board 
    def getOtherCards(self, cards, state):
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X']
        for i in cards:
            if i in letters:
                letters.remove(i)
        for i in state: 
            if i in letters: 
                letters.remove(i)
        return letters 


    def minimax(self, state, cards, constraints, depth, isMaximizing):
        bestMove = (0, 0)
        score = self.getScore(state, cards, constraints)
        curr_time = time.process_time() - self.time
        # check what the score is/ who the "winner" is 
        if depth == 8 or curr_time >= 1:
            score = self.getScore(state, cards, constraints)
            return bestMove, score

        state_array = np.array(state)
        available_hours = np.where(state_array == 'Z')
        # print("STATE:", state)
        # print("STATE ARR:", state_array)
        avail_arr = available_hours[0].flatten()
        # print("BEFORE", available_hours)
        # print("FLATTEN", avail_arr)
        # print("FLATTEN[0]: ", avail_arr[0])
        
        #maximizing
        if(isMaximizing):  
            bestScore = float('-inf')
            for i in avail_arr:
                for x in cards:
                    if x not in state:
                        state[i] = x
                        #print("STATE:", state)
                        #print("POS: ", i, "LETTER: ", x)
                        #we got rid of the plus sign here.....
                        score = self.minimax(state, cards, constraints, depth+1, False)[1]
                        state[i] = 'Z'
                        if (score>bestScore):
                            bestScore = score
                            bestMove = [i, x]
                            return bestMove, score

        #minimizing 
        #figure out how to minimize twice to represent the two players
        #add alpha beta
        else:
            bestScore = float('inf')
            other_cards = self.getOtherCards(cards, state)
            for i in avail_arr:
                for x in other_cards:
                    if x not in state:
                        state[i] = x
                        score = self.minimax(state, cards, constraints, depth+1, True)[1]
                        state[i] = 'Z'
                        if (score<bestScore):
                            bestScore = score
                            bestMove = [i,x]
                    
        
        return bestMove, score
        

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

        # print("STATE: ", state)
        # print("CARDS: ", cards)

        self.time = time.process_time()
        new_cards = cards.copy() 
        new_state = state.copy()
        new_constraints = constraints.copy()
        depth = 0
        
        bestMove = self.minimax(new_state, new_cards, new_constraints, depth, True)[0]
        #print("check: ", bestMove)
        letter= bestMove[1]
        hour = bestMove[0]
        hour = hour%12 if hour%12!=0 else 12
        return hour, letter
    
    # func to get the score of our own cards at the passed in state 
    def getScore(self, state, cards, constraints):
        # if a letter satsifies anything += 1/X, X being the number of letters in that constraint
        totalScore = 0
        score_arr = [0, 0, 1, 3, 6, 12]
        positions = {}
        # create dict of key letters to index values 
        for i in range(len(state)):
            positions[state[i]] = i
         
        for i in range(len(constraints) - 1):
            constraint = constraints[i].split('<')
            if constraint[i] in positions and constraint[i+1] in positions:
                position1 = positions[constraint[i]]
                position2 = positions[constraint[i+1]]
                difference = (position2%12) - (position1%12)
                if difference < 0:
                    difference += 12 
                if difference <= 5:
                    totalScore += float(score_arr[(len(constraint))]/len(constraint))
                else: 
                    totalScore -= 0.5
        
        #print("SCORE: ", totalScore)
        return totalScore    
