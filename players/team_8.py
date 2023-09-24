from dataclasses import dataclass
from tokenize import String
import numpy as np
import numpy.typing as npt
import random
import string
from typing import Tuple, List


@dataclass
class Node:
    state: npt.ArrayLike
    hour: int
    letter: str
    score: int = 0
    N: int = 0


class Tree:
    def __init__(self, root: "Node"):
        self.root = root
        self.root.children = []
        self.nodes = {root.state.tobytes(): root}

    def add(self, node: "Node"):
        self.nodes[node.state.tobytes()] = node
        self.root.children.append(node)

    def get(self, state: npt.ArrayLike):
        flat_state = state.tobytes()
        if flat_state not in self.nodes:
            return None
        return self.nodes[flat_state]


class Player:
    def __init__(self, rng: np.random.Generator) -> None:
        """Initialise the player with given skill.

        Args:
            rng (np.random.Generator): numpy random number generator, use this for same player behvior across run
        """
        self.rng = rng

    # def choose_discard(self, cards: list[str], constraints: list[str]):
    def choose_discard(self, cards, constraints, data_mode=None):
        """Function in which we choose which constraints to keep, and it also inititalises the cards dealt to the player at the game beginning

        Args:
            cards(list): A list of letters you have been given at the beginning of the game.
            constraints(list(str)): The total constraints assigned to the given player in the format ["A<B<V","S<D","F<G<A"].

        Returns:
            list[int]: Return the list of constraint cards that you wish to keep. (can look at the default player logic to understand.)
        """
        final_constraints = []

        for constraint in constraints:
            present_pct, alternating_pct = 0, 0
            lst = constraint.split("<")
            letters_in_constraint = set(lst)

            num_letters_in_cards = sum(
                1 for letter in letters_in_constraint if letter in cards)
            present_pct = (num_letters_in_cards / len(letters_in_constraint))

            if all(lst[i] in cards for i in range(0, len(lst), 2)) and len(letters_in_constraint) > 2:
                # [0, 2] in 3; [0, 2] in 4; [0, 2, 4] in 5
                alternating_pct = 0.6
            if all(lst[i] in cards for i in range(1, len(lst), 2)):
                if len(letters_in_constraint) > 2 and len(letters_in_constraint) % 2 == 1:
                    # [1] in 3; [1, 3] in 5
                    alternating_pct += 0.4
                elif len(letters_in_constraint) > 2:
                    # [1, 3] in 4
                    if alternating_pct == 0:
                        alternating_pct += 0.6
                    else:
                        # in case this is a 4/4
                        alternating_pct += 0.4

            pct = present_pct * 0.5 + alternating_pct * 0.5
            if pct >= 0.4:
                final_constraints.append(constraint)

            if data_mode:
                with open("data.txt", "a") as file1:
                    # Writing data to a file
                    file1.write("\n" + constraint + " present: " + str(present_pct) +
                                " alt: " + str(alternating_pct) + " final pct: " + str(pct))
                    file1.flush()

            # print(constraint, "present:", present_pct, "alt:", alternating_pct, "final pct:", pct, "\n")
        return final_constraints

    def __risky_versus_safe():
        pass

    def __utility(self, constraints: list[str], final_state: list[str]):
        """Utility function that returns player's score after a single monte carlo simulation

        Args:
            final_state (list(str)): The simulated letters at every hour of the 24 hour clock
            constraints(list(str)): The constraints assigned to the given player

        Returns:
            int: player's core after a single monte carlo simulation
        """
        score_value_list = [
            1, 3, 6, 12]  # points for satisfying constraints on different lengths
        score = 0
        for i in range(len(constraints)):
            list_of_letters = constraints[i].split("<")
            constraint_true_indic = True
            for j in range(len(list_of_letters)-1):
                distance_difference = (final_state.index(
                    list_of_letters[j+1]) % 12) - (final_state.index(list_of_letters[j]) % 12)
                if distance_difference < 0:
                    distance_difference = distance_difference + 12
                if not (distance_difference <= 5 and distance_difference > 0):
                    constraint_true_indic = False
                if constraint_true_indic == False:
                    score = score - 1
                else:
                    score = score + score_value_list[len(list_of_letters) - 2]
        return score

    def __select(self, tree: "Tree", state: list[str], alpha: float = 1):
        """Starting from state, move to child node with the
        highest UCT value.

        Args:
            tree ("Tree"): the search tree
            state (list[str]): the clock game state
            alpha (float): exploration parameter [PERHAPS THIS CAN BE DETERMINED IN RISKY_VS_SAFE()?]
        Returns:
            state: the clock game state after best UCT move
        """

        max_UCT = 0.0
        move = state

        for child_node in tree.root.children:
            node_UCT = (child_node.score/child_node.N + alpha *
                        np.sqrt(tree.root.N/child_node.N))
            if node_UCT > max_UCT:
                max_UCT = node_UCT
                move = child_node

        return move

    def __expand(self, tree: "Tree", cards: list[str], state: list[str]):
        """Add all children nodes of state into the tree and return
        tree.

        Args:
            tree ("Tree"): the search tree
            cards (list[str]): cards from our player
            state (list[str]): the clock game state
        Returns:
            "Tree": the tree after insertion
        """

        for letter in cards:
            # add our letters in every hour available
            for i in range(0, 12):
                new_state = np.copy(state)
                if new_state[i] == 'Z':
                    new_state[i] = letter
                elif new_state[i+12] == 'Z':
                    # if hour already occupied, try index + 12
                    new_state[i+12] = letter
                else:
                    # if both slots of hour already occupied, continue
                    continue
                hour = 12 if i == 0 else i
                tree.add(Node(np.array(new_state), hour, letter, 0, 1))
        return tree

    def __simulate(self, tree: "Tree", state: npt.ArrayLike, constraints: list[str], remaining_cards: list[str]):
        """Run one game rollout from state to a terminal state using random
        playout policy and return the numerical utility of the result.

        Args:
            tree ("Tree"): the search tree
            state (list[str]): the clock game state
            constraints (list[str]): constraints our player wants to satisfy
            remaining_cards (list[str]): cards from all players not yet played

        Returns:
            "Tree": the search tree with updated scores
        """
        new_state = np.copy(state)
        while len(remaining_cards):
            rand_letter = remaining_cards.pop(
                random.randint(0, len(remaining_cards) - 1))
            available_hours = np.where(new_state == 'Z')
            hour = random.choice(available_hours[0])
            new_state[hour] = rand_letter

        score = self.__utility(constraints, new_state.tolist())
        cur_node = tree.get(state)
        cur_node.score += score
        cur_node.N += 1
        tree.root.score += score
        tree.root.N += 1

        return tree

    def __MCTS(self, cards: list[str], constraints: list[str], state: list[str], rollouts: int = 1000):
        # MCTS main loop: Execute MCTS steps rollouts number of times
        # Then return successor with highest number of rollouts
        tree = Tree(Node(np.array(state), 24, 'Z', 0, 1))
        tree = self.__expand(tree, cards, state)
        possible_letters = list(string.ascii_uppercase)[:24]
        for letter in state:
            if letter != 'Z':
                possible_letters.remove(letter)

        for i in range(rollouts):
            available_letters = possible_letters.copy()
            move = self.__select(tree, state)
            available_letters.remove(move.letter)
            tree = self.__simulate(
                tree, move.state, constraints, available_letters)

        nxt = None
        plays = 0

        for succ in tree.root.children:
            if succ.N > plays:
                plays = succ.N
                nxt = succ
        return nxt

    # def play(self, cards: list[str], constraints: list[str], state: list[str], territory: list[int]) -> Tuple[int, str]:

    def play(self, cards, constraints, state, territory):
        """Function which based n current game state returns the distance and angle, the shot must be played

        Args:
            score (int): Your total score including current turn
            cards (list): A list of letters you have been given at the beginning of the game
            state (list[str]): The current letters at every hour of the 24 hour clock
            territory (list[int]): The current occupiers of every slot in the 24 hour clock. 1,2,3 for players 1,2 and 3. 4 if position unoccupied.
            constraints(list[str]): The constraints assigned to the given player

        Returns:
            Tuple(int, str): Return a tuple of slot from 1-12 and letter to be played at that slot
        """
        move = self.__MCTS(cards, constraints, state)
        return move.hour, move.letter
