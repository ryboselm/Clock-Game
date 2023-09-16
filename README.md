# Project 1: Clock Game

## Citation and License
This project belongs to Department of Computer Science, Columbia University. It may be used for educational purposes under Creative Commons **with proper attribution and citation** for the author TA **Akshay Iyer, and the Instructor, Prof. Kenneth Ross**.

## Summary

Course: COMS 4444 Programming and Problem Solving (Fall 2023)  
Problem Description: http://www.cs.columbia.edu/~kar/4444f23/node18.html
Course Website: http://www.cs.columbia.edu/~kar/4444f23/4444f23.html
University: Columbia University  
Instructor: Prof. Kenneth Ross  
Project Language: Python




### TA Designer for this project

1. Akshay Iyer

### Teaching Assistants for Course
1. Akshay Iyer
2. Smrithi Prakash





## Installation

Requires **python3.9** or higher

Install simulator packages only

```bash
pip install -r requirements.txt
```

## Usage

### Simulator

```bash
bash clock_game.sh False seed_number
```

Simulator Scheme : Player 1 always plays in black, player 2 always plays in blue, and player 3 always plays in red.
All entries in the clock will be masked if a player has not chosen their constraints yet.

If you decide to end the simulator prematurely, press Control+D to terminate the bash script and then run your next command.

### Running without Simulator

```bash
bash clock_game.sh True seed_number
```

You can change the random seed, number of constraints per player and timeout by changing the values inside constants.py.
