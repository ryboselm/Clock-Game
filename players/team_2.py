from tokenize import String
import numpy as np
from typing import Tuple, List

class Player:
    def __init__(self, rng: np.random.Generator) -> None:
        """Initialise the player.

        Args:
            rng (np.random.Generator): numpy random number generator, use this for same player behvior across run
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
        for constraint in constraints:
            constraint_letters = constraint.split('<')
            keep = True
            for i in range(len(constraint_letters) - 1):
                if (constraint_letters[i] not in cards and constraint_letters[i + 1] not in cards):
                    keep = False
            if keep:
                final_constraints.append(constraint)
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

        # Implemented Part 1
        discard = []
        useful = []
        
        allconstraints = ""
        for constraint in constraints:
            allconstraints += constraint

        for letter in cards:
            if letter in allconstraints:
                useful.append(letter)
            else:
                discard.append(letter)
        
        print('state:', state)
        print('territory:', territory)

        # Implemented Part 2
        chosen_hour = chosen_letter = None
        for constraint in sorted(map(lambda c: c.split('<'), constraints), key=len, reverse=True):
            repr = ''
            repr += 'EE'
            for letter in constraint:
                if letter in cards:
                    repr += 'O'
                elif letter in state:
                    repr += 'P'
                else:
                    repr += '_'
            repr += 'EE'
            for i in range(2, len(repr) - 2):
                if repr[i] != 'O':
                    continue
                if (repr[i-1] in ['P', 'E'] or repr[i-2:i] in ['EO', 'PO', 'OO']) and (repr[i+1] in ['P', 'E'] or repr[i-2] in ['OE', 'OP', 'OO']):
                    chosen_letter = constraint[i-2]
                    if repr[i-1] == 'P':
                        direction = 1
                        neighbor_letter = constraint[i-3]
                    elif repr[i+1] == 'P':
                        direction = -1
                        neighbor_letter = constraint[i-1]
                    else:
                        # TODO: Handle the other cases
                        continue
                    neighbor_index = state.index(neighbor_letter)
                    chosen_index = neighbor_index % 12 + direction
                    for _ in range(10):
                        if territory[chosen_index] == 4:
                            break
                        if direction == 1:
                            chosen_index = (chosen_index + (12 if chosen_index < 12 else -11)) % 24
                        else:
                            chosen_index = (chosen_index + (11 if chosen_index < 12 else -12)) % 24
                    if territory[chosen_index] != 4:
                        # TODO: This case should be handled earlier
                        continue
                    chosen_hour = chosen_index % 12 if chosen_index % 12 != 0 else 12
                    print(chosen_hour, chosen_letter)
                    return chosen_hour, chosen_letter

        # Implement Part 3 below
        # If this area of the code has been reached, then we couldn't find a useful we want to play
        if discard:
            chosen_letter = self.rng.choice(discard)
            chosen_hour = self.rng.choice([i for i in range(1, 13) if territory[i-1] == 4])
            return chosen_hour, chosen_letter
        # If there's no discard, then we have to play a useful, starting from the shortest constraint
        else:
            chosen_letter = None
            for constraint in sorted(map(lambda c: c.split('<'), constraints), key=len, reverse=False):
                for letter in useful:
                    if letter in constraint:
                        chosen_letter = letter
                        break
            available_hours = np.where(np.array(territory) == 4)
            chosen_hour = self.rng.choice(available_hours[0])
            return chosen_hour, chosen_letter



        # Remove this code block when done
        chosen_letter = self.rng.choice(cards)
        territory_array = np.array(territory)
        available_hours = np.where(territory_array == 4)
        chosen_hour = self.rng.choice(available_hours[0])
        chosen_hour = chosen_hour%12 if chosen_hour%12!=0 else 12
        return chosen_hour, chosen_letter
