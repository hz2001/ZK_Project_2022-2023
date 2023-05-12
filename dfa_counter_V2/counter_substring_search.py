### Must run with miniwizpl environment

from miniwizpl import *
from miniwizpl.expr import *
from functools import reduce



def stateCal(s: tuple) -> int:
    """
    Takes in a state (in tuple format) and return a unique hash of that word in integer 

    Args:
        s (tuple): A state in the DFA, e.g. (0,1,0)

    Returns:
        int: a unique integer representation of that state
    """
    result = 0
    for i in range(len(s)):
        result += (s[i] << 8 * i)
    return result

def incrementCounterList(state: tuple) -> None:
    """
    This function takes in a state, increament the counter based on the counterDict

    Args:
        state (tuple): a state within the dfa, with format tuple(tuple, word)
    """
    global counterList
    global counterDict
    if state in counterDict:
        toIncrement = counterDict[state]
        counterList = [toIncrement[i] + counterList[i] for i in range(len(counterList))]
    return 

def run_dfa(dfa: dict, document, zeroState):
    """
    This function is used to run the built DFA. 
    Takes in a dfa, a document to be run, and a correctly 
    formmated zeroState. 
    Returns the counterList that takes count of the coutners of each term in the target list.

    Args:
        dfa (dict): The DFA dictionary.
        document (str): string-like, the target document as plain text.
        zeroState (tuple): The default state of the DFA.
    """
    def next_state_fun(word, initial_state):
        '''
            I changed this part, otherwise when two sub texts are not contonious,
            the DFA never moves from the zero state
        '''
        curr_state = initial_state

        for (dfa_state, dfa_word), next_state in dfa.items():
            print(
                "curr state: ", val_of(curr_state),
                "dfa state: ", dfa_state,"\n",
                "input string: ", val_of(word),
                "dfa string: ", dfa_word,"\n",
                "next_state", next_state,"\n")
            # transform all tuples to numbers
            dfa_state = stateCal(dfa_state)
            next_state = stateCal(next_state)
            
            curr_state = mux((initial_state == dfa_state) & (word == dfa_word),
                             next_state,
                             curr_state)
            # Break out of the loop when finding the correct state & word, 
            # this will also allow us to use the latest tuple for counter
            break 
        
        incrementCounterList(state = (dfa_state, dfa_word))
        global counterList
        print(f"coutnerList = {counterList}") # TODO: Does counterList have to be secret as well??
        
        # print("initial state: ", val_of(initial_state), "current state: ", val_of(curr_state), "\n")
        # return curr_state since we are using reduce() for the loop
        return curr_state

    reduce(next_state_fun, document)
    return counterList


