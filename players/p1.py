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
        print(constraints)

        for i in range(len(constraints)):
            taking = True
            arr = constraints[i].split('<')
            for j in range(len(arr)-1):
                if arr[j] not in cards and arr[j+1] not in cards:
                    taking = False
            if taking:
                final_constraints.append(constraints[i])

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
        #calculates which constraints have the highest EVs
        constraint_scores = []
        for constraint in constraints:
            constraint_scores.append(self.calculate_ev(constraint, cards, state, territory))
        
        #constraint scores
        # print("Constraints:")
        # for i in range(len(constraints)):
        #     print(constraints[i]+": " + str(constraint_scores[i]))

        cscores = np.array(constraint_scores)
        ii = np.where(cscores == max(constraint_scores))[0]
        best_constraint = constraints[self.rng.choice(ii)]      #randomly samples a maximum EV constraint (if there are multiple).

        #if every constraint is unlikely to work right now, just stall by doing something random (may cannibalize other constraints for now)
        if (max(constraint_scores) < 0):
            best_constraint = "stall"
        
        print("best constraint to prioritize: ", best_constraint)

        #Do we want intermediate scores also available? Confirm pls
        # print(state)
        # print(territory)

        if best_constraint == "stall":                          #pick randomly, this is not ideal.
            letter = self.rng.choice(cards)
            territory_array = np.array(territory)
            available_hours = np.where(territory_array == 4)
            hour = self.rng.choice(available_hours[0])          #because np.where returns a tuple containing the array, not the array itself
            hour = hour%12 if hour%12!=0 else 12
            return hour, letter
        else:
            territory_array = np.array(territory)
            available_hours = np.where(territory_array == 4)[0]
            letters = best_constraint.split('<')
            lpos = [] # lpos: list(int): 1 through 12 for positions on the clock. 0 for in your hand. -1 for in opponent hand.
            for letter in letters:
                if letter in cards:
                    lpos.append(0)
                elif letter in state:
                    lpos.append(state.index(letter)%12 if state.index(letter)%12!=0 else 12)
                else:
                    lpos.append(-1)

            #greedily search for subconstraints it could potentially satisfy
            for i in range(len(lpos)):

                if i < len(lpos)-1:
                    if lpos[i] == 0 and lpos[i+1] > 0: #left constraint available, greedily takes a random satisfying spot.
                        checklist = self.five_indices(lpos[i+1], True)
                        #checklist is a list of the spots you could place that would satisfy the constraint, if they were open
                        spots = self.intersection(checklist, available_hours) #available and satisfying, if possible
                        if len(spots)>0:
                            hour = self.rng.choice(spots)
                            hour = hour%12 if hour%12!=0 else 12
                            return hour, letters[i]
                if i > 0:
                    if lpos[i-1] > 0 and lpos[i] == 0: #right constraint available, try to fill it
                        checklist = self.five_indices(lpos[i-1], False)
                        spots = self.intersection(checklist, available_hours) #available and satisfying, if possible
                        if len(spots)>0:
                            hour = self.rng.choice(spots)
                            hour = hour%12 if hour%12!=0 else 12
                            return hour, letters[i]
            
            #pick a totally random spot if no obvious spots were available. to refine later. 
            letter = self.rng.choice(cards)
            hour = self.rng.choice(available_hours)          #because np.where returns a tuple containing the array, not the array itself
            hour = hour%12 if hour%12!=0 else 12
            return hour, letter


    def calculate_ev(self, constraint, cards, state, territory):
        """
            calculates a heuristic EV of a given constraint
        """
        arr = constraint.split('<')
        returns = [1,3,6,12]
        win_value = returns[len(arr)-2] # the value received if this constraint is satisfied
        avail_spots = state.count('Z') # the total number of open spaces left on the board.

        # letter_positions: list(int): 1 through 12 for positions on the clock. 0 for in your hand. -1 for in opponent hand.
        letter_positions = []
        for letter in arr:
            if letter in cards:
                letter_positions.append(0)
            elif letter in state:
                letter_positions.append(state.index(letter)%12 if state.index(letter)%12!=0 else 12)
            else:
                letter_positions.append(-1)
        print(letter_positions)
        probability = 1.0
        moves_needed = letter_positions.count(0)
        validPlacements = [list(range(24)) for i in range(len(arr))] # a list of lists showing the valid placement spots of each of the potential letters

        for i in range(len(letter_positions)-1):
            if letter_positions[i] > 0 and letter_positions[i+1] > 0: #both letters present on clock
                diff = letter_positions[i+1] - letter_positions[i]
                if diff>0 and diff<=5 or diff<=-7:
                    continue #constraint is satisfied, do not need to reduce letter placements
                else: #this constraint is already violated, cannot be satisfied
                    return -100000
                
            elif letter_positions[i] == -1 and letter_positions[i+1] > 0: #unpossessed first letter
                checklist = self.five_indices(letter_positions[i+1],True)
                validPlacements[i] = self.intersection(validPlacements[i], checklist)

            elif letter_positions[i] > 0 and letter_positions[i+1] == -1: #unpossessed second letter
                checklist = self.five_indices(letter_positions[i], False)
                validPlacements[i+1] = self.intersection(validPlacements[i+1], checklist)
            
            elif letter_positions[i] == -1 and letter_positions[i+1] == -1: # both missing, but not fixed down
                continue
            elif letter_positions[i] == -1 and letter_positions[i+1] == 0:
                continue
            elif letter_positions[i] == 0 and letter_positions[i+1] == -1:
                continue
            #todo: consider the cases where 2 in a row are missing.

        for i in range(len(letter_positions)):
            if letter_positions[i] == -1:
                Zcount = 0
                for j in validPlacements[i]:
                    if territory[j] == 'Z':
                        Zcount = Zcount + 1
                probability *= Zcount/avail_spots
        
        if probability <= 0: #unwinnable
            return -100000
        EV = probability*win_value + (1-probability)*(-1)
        if moves_needed > 0:
            return EV
        else: #already finished placing, disregard
            return -100000
    
    #helper function
    def intersection(self, lst1, lst2):
        lst3 = [value for value in lst1 if value in lst2]
        return lst3
    
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