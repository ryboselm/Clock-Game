import subprocess
import numpy as np

rng_generator = np.random.default_rng(16) #seeds the randomness of the randomness
rounds = 5
players = [5, 0, 0]
num_constraints = 30
rng_list = rng_generator.integers(100000, size=100)
#games go off of the exact same seeds as one another, but with different parameters
param_search = False #control whether to do param search as below or just test one param thing
if param_search:
    for low in np.arange(0.2, 0.41, 0.1):
        for mid in np.arange(0.5, 0.81, 0.1):
            for high in np.arange(0.8, 1.01, 0.1):
                params = [round(low,2), round(mid,2), round(high,2)]
                #print(params)
                total_points = 0

                for i in range(rounds):
                    rng = rng_list[i]
                    result = subprocess.run(["python", "clock_game.py", "-ng", "True", "-s", str(rng), "--myparams", str(params[0]), str(params[1]), str(params[2]), str(num_constraints), "--myplayers", str(players[0]), str(players[1]), str(players[2])], stdout=subprocess.PIPE, text=True)
                    total_points += int(result.stdout)
                    #print(result.stdout)
                    #print(i)
                print("params:", params, "avg score after", rounds, "rounds:", total_points / rounds)
                with open("testing_log.txt", 'a' ) as f:
                        f.write("params: " + str(params) + " avg score after " + str(rounds) + " rounds: " + str(total_points / rounds))
                        f.write('\n')
else:
    params = [0.43, 0.17, 0.95]
    rng_list = rng_generator.integers(100000, size=100)
    for num_constraints in range(15,30, 10):
        total_points = 0
        wins = 0
        rounds = 20
        for i in range(rounds):
            rng = rng_list[i]
            result = subprocess.run(["python", "clock_game.py", "-ng", "True", "-s", str(rng), "--myparams", str(params[0]), str(params[1]), str(params[2]), str(num_constraints), "--myplayers", str(players[0]), str(players[1]), str(players[2])], stdout=subprocess.PIPE, text=True)
            results = result.stdout.split(" ")
            total_points += int(results[0])
            if int(results[1]) == 1: #player 1 won
                 wins+=1
            print(result.stdout)
            print(i)
        print("params:", params, "num constraints:", num_constraints, "avg score and winning prob. after", rounds, "rounds:", total_points / rounds, wins/rounds)
        with open("testing_log2.txt", 'a' ) as f:
                f.write("params: " + str(params) + ", num constraints: " + str(num_constraints) + ", avg score and winning prob. after " + str(rounds) + " rounds: " + str(total_points / rounds) + " " + str(wins/rounds))
                f.write('\n')