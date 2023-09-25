import subprocess
import numpy as np

rng_generator = np.random.default_rng(1453)
rounds = 5
players = [5, 0, 0]
rng_list = rng_generator.integers(100000, size=100)
#games go off of the exact same seeds as one another, but with different parameters

for low in np.arange(0.2, 0.41, 0.1):
    for mid in np.arange(0.5, 0.81, 0.1):
        for high in np.arange(0.8, 1.01, 0.1):
            params = [round(low,2), round(mid,2), round(high,2)]
            #print(params)
            total_points = 0

            for i in range(rounds):
                rng = rng_list[i]
                result = subprocess.run(["python", "clock_game.py", "-ng", "True", "-s", str(rng), "--myparams", str(params[0]), str(params[1]), str(params[2]), "--myplayers", str(players[0]), str(players[1]), str(players[2])], stdout=subprocess.PIPE, text=True)
                total_points += int(result.stdout)
                #print(result.stdout)
                #print(i)
            print("params:", params, "avg score after", rounds, "rounds:", total_points / rounds)
            with open("testing_log.txt", 'a' ) as f:
                    f.write("params: " + str(params) + " avg score after " + str(rounds) + " rounds: " + str(total_points / rounds))
                    f.write('\n')

#params = [0.2, 0.7, 0.9]

# rng_list = rng_generator.integers(100000, size=100)
# total_points = 0

# for i in range(rounds):
#     rng = rng_list[i]
#     result = subprocess.run(["python", "clock_game.py", "-ng", "True", "-s", str(rng), "--myparams", str(params[0]), str(params[1]), str(params[2]), "--myplayers", str(players[0]), str(players[1]), str(players[2])], stdout=subprocess.PIPE, text=True)
#     total_points += int(result.stdout)
#     #print(result.stdout)
#     print(i)
# print("params:", params, "avg score after", rounds, "rounds:", total_points / rounds)
# with open("testing_log.txt", 'a' ) as f:
#         f.write("params: " + str(params) + " avg score after " + str(rounds) + " rounds: " + str(total_points / rounds))
#         f.write('\n')