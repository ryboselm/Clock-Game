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

    def ev(self, constraints: list[str], hand: list[str]):
        value = dict()
        # evaluating the expected payoff of each constraint
        for formatted_constraint in constraints:
            constraint = formatted_constraint.replace("<", "")
            p = 1.0
            for letter in hand:
                idx = constraint.find(letter)
                if idx != -1:
                    if (idx > 0 and constraint[idx-1] not in hand)\
                    and (idx < len(constraint)-1 and constraint[idx+1] not in hand):
                        p *= 0.94
            for idx in range(1, len(constraint)):
                if (constraint[idx-1] not in hand) and (constraint[idx] not in hand):
                    p *= 10/23
                else:
                    p *= 0.98
            print(f"constraint: {formatted_constraint}")
            print(f"p={p:.5f}")
            value[formatted_constraint] = 2.0*p-1.0 if len(constraint) == 2 else p-1+p*3.0*2**(len(constraint)-3)
            print(f"ev={value[formatted_constraint]:.5f}")

        return value
    
    #def choose_discard(self, cards: list[str], constraints: list[str]):
    def choose_discard(self, cards, constraints):
        """Function in which we choose which cards to discard, and it also inititalises the cards dealt to the player at the game beginning

        Args:
            cards(list): A list of letters you have been given at the beginning of the game.
            constraints(list(str)): The total constraints assigned to the given player in the format ["A<B<V","S<D","F<G<A"].

        Returns:
            list[int]: Return the list of constraint cards that you wish to keep. (can look at the default player logic to understand.)
        """
        value = self.ev(constraints, cards)
        sorted_constraints_dict = dict(sorted(value.items(), key=lambda item: item[1], reverse=True))
        print("sorted constraints:", sorted_constraints_dict)

        final_constraints = []
        for formatted_constraint, ev in sorted_constraints_dict.items():
            if ev > 0:
                final_constraints.append(formatted_constraint)

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

        letter = self.rng.choice(cards)
        territory_array = np.array(territory)
        available_hours = np.where(territory_array == 4)
        hour = self.rng.choice(available_hours[0])          #because np.where returns a tuple containing the array, not the array itself
        hour = hour%12 if hour%12!=0 else 12
        return hour, letter
