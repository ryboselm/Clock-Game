import copy

import numpy as np
from tokenize import String
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

        self.curr_constraint_tally = None

    def constraint_parser(self, _constraint):
        """A function that converts a constraint in string format to a list format.

        Args:
            _constraint(string) : The input string in the format "A<B<C".

        Returns:
            list[str] : Return a string in the form of ["A", "B", "C"]
        """
        return _constraint.upper().split('<')

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
        # print("Constraints given to us:", constraints)
        # print("Cards given to us:", cards)


        def assign_score_to_const(_constraint, _cards):

            """Function to assign a score based on expected reward to risk involved in picking the constraint at the beggining of the game.

            Args:
                _constraint(string) : a string containing the current constraint for which the score needs to be computed.
                _cards(list) : A list of letters given at the beginning of the same.

            Returns:
                score(int) : A score assigned to the constraint based on its feasibility and score obtained if the constraint is satisfied.
            """

            # A dict keeping hardcoded probabilities for the three cases of two letter constraints
            two_letter_probs = {0: 0.43478260869, 1: 0.75, 2: 1}

            # Points associated with each constraint size
            points_for_consts = {2: 1, 3: 3, 4: 6, 5: 12}

            # print("Current constraint:", _constraint)
            lst_constraint = self.constraint_parser(_constraint)
            # print("List format constraint:", lst_constraint)

            score = 1
            for i in range(len(lst_constraint) - 1):
                if lst_constraint[i] in _cards and lst_constraint[i+1] in _cards:
                    score *= two_letter_probs[2]

                elif (lst_constraint[i] in _cards and lst_constraint[i+1] not in _cards) or (lst_constraint[i] not in _cards and lst_constraint[i+1] in _cards):
                    score *= two_letter_probs[1]

                else:
                    score *= two_letter_probs[0]

            return score * points_for_consts[len(lst_constraint)] - (1-score)


        # loop over all the constraints
        for curr_const in constraints:
            curr_const_score = (assign_score_to_const(curr_const, cards))
            # print("Score assigned to current constraint is", curr_const_score)
            if curr_const_score  >= 0:
                final_constraints.append(curr_const)

        self.curr_constraint_tally = {const: False for const in final_constraints}

        # print("Final selected constraints:", final_constraints)
        return final_constraints

    def is_2_const_satisfied(self, _two_const, _state):
        """A Function that checks whether a two letter constraint is satisfied.

        Args:
            _two_const (tuple(str, str)): A tuple containing two letter constraint.
            _state (list(list)): The state of the clock.

        Returns:
            bool: A boolean value that descibes whether the two letter constraint is satisfied.
        """

        # print("\t\tCurrent 2 letter constraint to evaluate is `{}<{}'".format(_two_const[0], _two_const[1]))

        # Obtain the index of left and right elements of the constraint
        l_idx = _state.index(_two_const[0]) 
        r_idx = _state.index(_two_const[1])

        # print("\t\tleft and right indices", l_idx, r_idx)

        if ((l_idx // 2) + 7) % 12 > ((r_idx // 2) + 1) % 12:
            return True
        return False


    def is_constraint_satisfied(self, _card, _card_placement, _constraints, state, territory):
        """Function which checks if a card move with help improve the constraint condition.

        Args:
            _card (str): A string depicting which card is being considered to play currently.
            _card_placement (int): A number between 0-23 that describes the position of the card.
            state (list(list)): The current letters at every hour of the 24 hour clock
            territory (list(int)): The current occupiers of every slot in the 24 hour clock. 1,2,3 for players 1,2 and 3. 4 if position unoccupied.
            _constraints(str): The constraints selected before the start of the game

        Returns:
            int: Return an int that describes if a placement satisfies the constraint (even if partially). 1 - if constraint is helped by the move, 0 - neutral case, -1 - if the move is against the constraint
        """


        # print("Current move is to play card {} to position {}".format(_card, _card_placement))
        # print("_constraints", _constraints)

        # Obtain all the constraints that are affected by current card
        _rel_constraints = [_const for _const in _constraints if _card in _const]
        
        # print("_rel_constraints", _rel_constraints)
        
        # Return if no constraint is affected by this card
        if len(_rel_constraints) == 0:
            return 0
        
        _const_status = [True] * len(_rel_constraints)

        for idx, _const in enumerate(_rel_constraints):

            # print("\tLooking into constraint ", _const)
            lst_const = self.constraint_parser(_const)

            # Check if the contraint so far has been satisfied
            for i in range(len(lst_const) - 1):
                if lst_const[i] == _card and lst_const[i+1] in state:
                    # Check if placing the current card at its respective place will satisfy the "`_card'<`right_card'" constraint.
                    temp_state = copy.deepcopy(state)
                    temp_state[_card_placement] = _card
                    
                    # if constraint is not satisfied, then skip to the next constraint
                    if self.is_2_const_satisfied((_card, lst_const[i+1]), temp_state) is False:
                        _const_status[idx] = False
                        break
                
                elif lst_const[i] == _card and lst_const[i+1] not in state:
                    # if the next card is not present, just continue to the next index
                    # Look into this case later on!
                    continue
                        
                elif lst_const[i] in state and lst_const[i+1] == _card:
                    # Check if placing the current card at its respective place will satisfy the "`left_card'<`_card'" constraint.
                    temp_state = copy.deepcopy(state)
                    temp_state[_card_placement] = _card
                    
                    # if constraint is not satisfied, then skip to the next constraint
                    if self.is_2_const_satisfied((lst_const[i], _card), temp_state) is False:
                        _const_status[idx] = False
                        break

                elif lst_const[i] not in state and lst_const[i+1] == _card:
                    # if the next card is not present, just continue to the next index
                    # Look into this case later on!
                    continue
                
                elif lst_const[i] in state and lst_const[i+1] in state:
                    # if constraint is not satisfied, then skip to the next constraint
                    if self.is_2_const_satisfied((lst_const[i], lst_const[i+1]), state) is False:
                        _const_status[idx] = False
                        break

        # print("_const_status at the end", _const_status)

        if np.any(_const_status):
            return 1
        else:
            return -1


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
        # Do we want intermediate scores also available? Confirm pls
        
        # print("\n***\n")
        
        #print("State: ", state)
        #print("Territory: ", territory)
        # print("Current Constraint Tally", self.curr_constraint_tally)

        max_iter = 1000
        for i in range(max_iter):

            letter = self.rng.choice(cards)
            territory_array = np.array(territory)
            available_hours = np.where(territory_array == 4)
            hour = self.rng.choice(available_hours[0])          # because np.where returns a tuple containing the array, not the array itself

            # Check if current random play leads to any constraint's situation improving
            is_satisfied = self.is_constraint_satisfied(letter, hour, constraints, state, territory)
            if is_satisfied == 1:
                break
        
        # print("~~~~~~~~~~~Is Satisfied: ", is_satisfied, "~~~~~~~~~~~~~~~")

        hour = hour % 12 if hour % 12 != 0 else 12
        return hour, letter
