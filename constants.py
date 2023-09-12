import os
import argparse 

timeout = 10 # 10s aggregate time limit
number_of_constraints_pp = 5
c = 10
exact_pos = 20
rng_seed = 5



"""if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--seed",
        "-s",
        type=int,
        default=2,
        help="Seed used by random number generator, specify 0 to use no seed and have different random behavior on each launch",
    )
    parser.add_argument("--no_gui", "-ng", default = False, help="Disable GUI")
    parser.add_argument("--num_constraints", "-nc", default = False, help="Choose Number of constraints per player")
    parser.add_argument("--timeout", "-t", default = False, help="Time when exceeded will terminate the app")
    args = parser.parse_args()
    
    rng_seed = args.seed
    timeout = args.timeout
    no_gui = args.no_gui
    number_of_constraints_pp = args.num_constraints"""