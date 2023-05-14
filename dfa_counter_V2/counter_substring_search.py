# Must run with miniwizpl environment

from miniwizpl import *
from miniwizpl.expr import *
# from functools import reduce # we are not using reduce from functools, seems that we are using the one from miniwizpl
from .counter_dfa_builder import stateCal
from .global_vars import counterDict, counterList


def incrementCounterList(state: tuple) -> None:
    """
    This function takes in a state, increament the counter based on the counterDict

    Args:
        state (tuple): a state within the dfa, with format tuple(tuple, word)
    """
    global counterDict
    global counterList
    if state in counterDict:
        toIncrement = counterDict[state]
        counterList = [toIncrement[i] + counterList[i]
                                   for i in range(len(counterList))]
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
        zeroState (tuple): The default state of the DFA. """

    def next_state_fun(word, initial_state):
        '''
            I changed this part, otherwise when two sub texts are not contonious,
            the DFA never moves from the zero state
        '''
        # go to zeroState always, unless we have the next state in the DFA
        curr_state = zeroState

        for (dfa_state, dfa_word), next_state in dfa.items():
            print(
                "curr state: ", val_of(curr_state),
                "dfa state: ", dfa_state, "\n",
                "input string: ", val_of(word),
                "dfa string: ", dfa_word, "\n",
                "next_state", next_state, "\n")
            # transform all tuples to numbers
            # TODO: Ask if I can do stateCal to the dfa before the run dfa, since I might have to use (dfa_state, dfa_word) for the counter increment as well. see line 60
            dfa_state = stateCal(dfa_state)
            next_state = stateCal(next_state)

            curr_state = mux((initial_state == dfa_state) & (word == dfa_word),
                             next_state,
                             curr_state)
            # Break out of the loop when finding the correct state & word,
            # this will also allow us to use the latest tuple for counter
            break

        # TODO: Problematic, now the dfa_state and dfa_word are calculated to be int, but the dict is still using tuples.
        incrementCounterList(state=(dfa_state, dfa_word))
        # global counterList
        # print(f"coutnerList = {counterList}") # TODO: Does counterList have to be secret as well??

        # print("initial state: ", val_of(initial_state), "current state: ", val_of(curr_state), "\n")
        # return curr_state since we are using reduce() for the loop
        return curr_state

    # try:
    #     itor1 = iter(document)
    # except TypeError as te:
    #     print("document", 'is not iterable')
    # try:
    #     itor2 = iter(zeroState)
    # except TypeError as te:
    #     print("zeroState", 'is not iterable')

    reduce(next_state_fun, document, zeroState)

    global counterList
    global counterDict
    # cleanup
    counterList = counterList.copy()
    counterDict = {}  # clear the output for the global counterDict
    counterList = []  # clear the output for the global counterList
    return counterList
