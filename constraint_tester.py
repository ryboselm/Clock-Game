from players.team_8 import *
from itertools import permutations


given_cards = ["A", "B", "C"]


def all_possible_constraints():
    # Generate combinations of 1 to 5 letters (as each letter appears only once)
    letters = ['A', 'B', 'C', 'D', 'E']
    all_permutations = []

    # Generate permutations of 2 to 5 letters (as each letter appears only once)
    for r in range(2, 6):
        # Generate all possible permutations
        for combo in permutations(letters, r):
            # Convert the permutation to a sorted string
            joined_combo = '<'.join(combo)
            all_permutations.append(joined_combo)

    # Convert the list of permutations to a set to remove duplicates
    unique_permutations = set(all_permutations)

    # Convert the set back to a list
    unique_permutations_list = list(unique_permutations)

    # Print the permutations
    # i = 1
    # for x in sorted(unique_permutations_list):
    #     print(i, x)
    #     i+=1
    return list(sorted(unique_permutations_list))


with open("data.txt", "a+") as file:
    # Move the file cursor to the beginning of the file
    file.seek(0)

    file_contents = file.read()

    if file_contents:   # If the file is not empty, clear its contents and write the data
        file.truncate(0)
    file.write(str(given_cards))

tester = Player(np.random.default_rng(int(4)))
print(tester.choose_discard(given_cards, all_possible_constraints(), True))
