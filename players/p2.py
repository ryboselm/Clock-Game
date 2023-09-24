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

    def conv_const(self, state, con, hand):
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

    def pick_slot(self, state, const, hand):
        # takes in converted constraint
        # pick letter to try
        highest = -1
        highest_i = 0
        highest_left = ('', '')
        highest_right = ('', '')
        if '1' not in const[1]:
            return (('', ''), -1)
        for i in range(len(const[0])):
            if const[1][i] == '1':
                score = 1
                score_left = ('', '')
                score_right = ('', '')
                if i != 0:
                    score = int(const[1][i - 1])
                    score_left = (const[0][i - 1], const[1][i - 1])
                if i != len(const[0]) - 1:
                    score *= int(const[1][i + 1])
                    score_right = (const[0][i + 1], const[1][i + 1])
                print(const[0][i], score)
                if score > highest:
                    highest = score
                    highest_i = i
                    highest_left = score_left
                    highest_right = score_right
        left_dep_slots = set()
        right_dep_slots = set()
        open_slots = []
        where = {}
        for i in range(len(state)):
            for j in state[i]:
                if j == 'Z':
                    open_slots.append(i)
                else:
                    where[j] = i
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
        valid_slots = right_dep_slots.intersection(left_dep_slots)
        print(valid_slots)
        if len(valid_slots) == 0:
            print(open_slots)
            print(hand)
            print(state)
            return ((open_slots[0],const[0][highest_i]), 0)
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
        #Do we want intermediate scores also available? Confirm pls
        top = 0
        top_i = 0
        inp = 0
        need = set()
        for strain in constraints:
            for_need = strain.split("<")
            for letter in for_need:
                need.add(letter)
            temper = self.conv_const( state, strain, cards)
            out = self.pick_slot( state, temper, cards)
            if out[1] > top:
                top = out[1]
                top_i = out
                inp = len(strain)
            if out[1] == top:
                if len(strain) > inp:
                    top = out[1]
                    top_i = out
                    inp = len(strain)
        disc = set(cards).difference(need)

        if top < 0.85 and len(disc) > 0:
            territory_array = np.array(territory)
            available_hours = np.where(territory_array == 4)
            hour = self.rng.choice(
                available_hours[0])  # because np.where returns a tuple containing the array, not the array itself
            hour = hour % 12 if hour % 12 != 0 else 12
            return hour, list(disc)[0]
        elif top_i[0][0] == -1:
            letter = self.rng.choice(cards)
            territory_array = np.array(territory)
            available_hours = np.where(territory_array == 4)
            hour = self.rng.choice(
                available_hours[0])  # because np.where returns a tuple containing the array, not the array itself
            hour = hour % 12 if hour % 12 != 0 else 12
            return hour, letter
        else:
            print(top_i[0])
            return(top_i[0])


