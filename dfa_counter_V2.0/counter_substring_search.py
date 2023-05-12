### Must run with miniwizpl environment

from miniwizpl import *
from miniwizpl.expr import *
from functools import reduce



def stateCal(s:tuple) -> int:
    """
    Takes in a state (in tuple format) and return a unique hash of that word in integer 

    Args:
        s (tuple): a word to be convereted

    Returns:
        int: a integer representation of that word 
    """
    result = 0
    for i in range(len(s)):
        result += (s[i] << 8 * i)
    return result

def incrementCounterList(state: tuple) -> None:
    global counterList
    global counterDict
    if state in counterDict:
        toIncrement = counterDict[state]
        counterList = [toIncrement[i] + counterList[i] for i in range(len(counterList))]
    return 

def run_dfa(dfa: dict, document, zeroState):
    def next_state_fun(word, initial_state):
        '''
            I changed this part, otherwise when two sub texts are not contonious,
            the DFA never moves from the zero state
        '''
        curr_state = initial_state

        for (dfa_state, dfa_word), next_state in dfa.items():
            # print(
            #     "curr state: ", val_of(curr_state),
            #     "dfa state: ", dfa_state,"\n",
            #     "input string: ", val_of(word),
            #     "dfa string: ", dfa_word,"\n",
            #     "next_state", next_state,"\n")
            # transform all tuples to numbers
            dfa_state = stateCal(dfa_state)
            next_state = stateCal(next_state)
            
            curr_state = mux((initial_state == dfa_state) & (word == dfa_word),
                             next_state,
                             curr_state)
            break
        incrementCounterList(state = (dfa_state, dfa_word))
        
        print("initial state: ", val_of(initial_state), "current state: ", val_of(curr_state), "\n")
        return curr_state

    latest_state = reduce(next_state_fun, document, zeroState)
    return latest_state


