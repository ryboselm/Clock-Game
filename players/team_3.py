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
        stripped_constraints = []
        #print("CONSTRAINTS")
        #print(constraints)

        #print("CARDS")
        #print(cards)

        for i in range(len(constraints)):
            # splits current constraint into array of letters and removes <'s 
            curr = constraints[i].split('<')
            while '<' in curr:
                curr.remove('<')
            numLetters = len(curr)
            
            # see how many letters in a constraint we have 
            matches = 0
            for letter in curr:
                if letter in cards:
                    matches += 1

            match numLetters:
                    case 2:
                        if(matches == 1) or (matches == 2):
                            final_constraints.append(constraints[i])
                    case 3:
                        if(matches == 2):
                            final_constraints.append(constraints[i])
                    case 4:
                        if(matches == 3):
                            final_constraints.append(constraints[i])
                        elif((curr[0] in cards and curr[2] in cards) or (curr[1] in cards and curr[3] in cards)):
                            final_constraints.append(constraints[i])
                    case 5:
                        if(matches == 4):
                            final_constraints.append(constraints[i])
                        elif((curr[0] in cards and curr[2] in cards and curr[4] in cards)):
                            final_constraints.append(constraints[i]) 

            # if we don't have any letters in a constraint don't choose it 

            #if(len(final_constraints) == 0){
            #}
  
            #if self.rng.random()<=0.5:
            #   final_constraints.append(constraints[i])

        #print("FINAL")
        #print(final_constraints)
        return final_constraints
    
    

    def is_played(self, letter, state):
        for i in range(len(state)):
            if letter in state[i]:
                return (True, i)
        return (False, -1)


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

        letter = self.rng.choice(cards)
        territory_array = np.array(territory)
        available_hours = np.where(territory_array == 4)
        hour = self.rng.choice(available_hours[0])          #because np.where returns a tuple containing the array, not the array itself
        hour = hour%12 if hour%12!=0 else 12

        #add code to sort arrays by len??
        #add code to highlight priority (short vs long term gain)
        #add code to remove constraints as they becomes unachievable

        for constraint in constraints:
            #print("constraint: ", constraint)
            numLetters = len(constraint)

            match numLetters:
                case 2:
                    if(self.is_played(constraint[0],state)[0] and constraint[1] in cards):
                        hour_played = self.is_played(constraint[0], state)[1]
                        shift = 1
                        while((hour_played + shift) not in available_hours):
                            shift+=1
                        hour = hour_played + shift
                        hour = hour%12 if hour%12!=0 else 12
                        letter = constraint[1]

                    elif(self.is_played(constraint[1],state)[0] and constraint[0] in cards):
                        hour_played = self.is_played(constraint[1], state)[1]
                        shift = -1
                        while((hour_played + shift) not in available_hours):
                            shift-=1
                        hour = hour_played + shift
                        hour = hour%12 if hour%12!=0 else 12
                        letter = constraint[0]

                    elif(constraint[0] in cards and constraint[1] in cards):
                        hour = 6 
                        shift = 0
                        while((hour_played + shift) not in available_hours):
                            shift-=1
                        hour = hour_played + shift
                        hour = hour%12 if hour%12!=0 else 12
                        letter = constraint[0]

                case 3:
                #if(matches == 2):
                #        final_constraints.append(constraints[i])

                    #If we have the middle letter (not played)
                    if(constraint[1] in cards):
                        
                        #If both the first and last letter have been played, play the middle letter in between them
                        if(self.is_played(constraint[0],state)[0] and self.is_played(constraint[2],state)[0]):
                            hour_played = self.is_played(constraint[0], state)[1]
                            hour_played2 = self.is_played(constraint[2], state)[1]

                            if(hour_played < hour_played2+1):
                                shift = 1
                                while((hour_played + shift) not in available_hours and hour_played+shift < hour_played2):
                                    shift+=1
                                hour = hour_played + shift
                                hour = hour%12 if hour%12!=0 else 12
                                letter = constraint[1]
                                    
                        #If only the first letter has been played, play the middle letter after it 
                        elif(self.is_played(constraint[0],state)[0]):
                            hour_played = self.is_played(constraint[0], state)[1]
                            shift = 1
                            while((hour_played + shift) not in available_hours):
                                shift+=1
                            hour = hour_played + shift
                            hour = hour%12 if hour%12!=0 else 12
                            letter = constraint[1]

                        #If only the last letter has been played, play the middle letter before it 
                        elif(self.is_played(constraint[2],state)[0]):
                            hour_played = self.is_played(constraint[2], state)[1]
                            shift = -1
                            while((hour_played + shift) not in available_hours):
                                shift-=1
                            hour = hour_played + shift
                            hour = hour%12 if hour%12!=0 else 12
                            letter = constraint[1]

                        #Neither first nor last letter has been played
                        else:
                            hour = 6 
                            shift = 0
                            while((hour_played + shift) not in available_hours):
                                shift-=1
                            hour = hour_played + shift
                            hour = hour%12 if hour%12!=0 else 12
                            letter = constraint[1]

                    #If middle letter has been played
                    if(self.is_played(constraint[1],state)[0]):
                        
                        if(self.is_played(constraint[0],state)[0]):
                            hour_played = self.is_played(constraint[0], state)[1]
                # case 4:
                # #if(matches == 3)
                #     played = []
                #     not_played = []
                #     num_played = 0
                #     # see how many are played of this constraint 
                #     for i in len(constraint):
                #         if(self.is_played(constraint[i], state)[0]):
                #             num_played += 1
                #             played.append(i)
                #         else: 
                #             not_played.append(i)

                #     if num_played == 3: 
                #         # check if you have the unplayed one 
                #         if(constraint[not_played[0]] in cards):
                #             letter = constraint[not_played[0]]

                #             hour_played = self.is_played(constraint[played[0]], state)[1]
                #             hour_played2 = self.is_played(constraint[played[1]], state)[1]
                #             hour_played3 = self.is_played(constraint[played[2]], state)[1]
                                        

                #     elif num_played == 2:
                #         if(constraint[not_played[0]] in cards):
                #             letter = constraint[not_played[0]]
                            
                #             hour_played = self.is_played(constraint[played[0]], state)[1]
                #             hour_played2 = self.is_played(constraint[played[1]], state)[1]
                #         elif(constraint[not_played[1]] in cards):
                #             letter = constraint[not_played[0]]
                            
                #             hour_played = self.is_played(constraint[played[0]], state)[1]
                #             hour_played2 = self.is_played(constraint[played[1]], state)[1]

                #     elif num_played == 1:
                #         pass

                #     else: # play any of the cards that you have in this constraint 
                #         if(constraint[0] in cards):
                #             letter = constraint[0]
                #             #hour = 


                #     if(self.is_played(constraint[0], state)[0] and self.is_played(constraint[1], state)[0] and self.is_played(constraint[3], state)[0]):
                #         hour_played = self.is_played(constraint[1], state)[1]
                #         hour_played2 = self.is_played(constraint[2], state)[1]
                #         hour_played3 = self.is_played(constraint[3], state)[1]


                # case 5: 
                # #if(matches == 4)

                #     #If we have the middle letter (not played)
                #     if(constraint[2] in cards):
                #         #If both the first and last letter have been played, play the middle letter in between them
                #         if(self.is_played(constraint[1],state)[0] and self.is_played(constraint[3],state)[0]):
                #             hour_played = self.is_played(constraint[1], state)[1]
                #             hour_played2 = self.is_played(constraint[3], state)[1]

                #             if(hour_played < hour_played2+1): #check if const[1] < const[3] if not then discard constraint and keep playing other ones.
                #                 shift = 1
                #                 while((hour_played + shift) not in available_hours and hour_played+shift < hour_played2):
                #                     shift+=1
                #                 hour = hour_played + shift
                #                 hour = hour%12 if hour%12!=0 else 12
                #                 letter = constraint[2]
                            

                #         #if

                                                  

                       


        return hour, letter
    
