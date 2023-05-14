# Author: Herbert Zhang
# This file contains everything that we need to build and run the dfa with counter.
# Must run with miniwizpl environment

from miniwizpl import *
from miniwizpl.expr import *
# from functools import reduce # we are not using reduce from functools, seems that we are using the one from miniwizpl
from .counter_dfa_builder import *
from .util import *

counterDict = {}
counterList = []

def stateCal(s: tuple) -> int:
    """
    Takes in a state of the DFA (in tuple format) and return a unique 
    hash of that word in integer

    Args:
        s (tuple): A state in the DFA, e.g. (0,1,0)

    Returns:
        int: a unique integer representation of that state
    """
    result = 0
    for i in range(len(s)):
        result += s[i] << 8 * i
    return result


def word_to_integer_string(word_to_convert: str) -> str:
    """The same functionlity as word_to_integer, 
    except that we express the integer as type string"""
    return str(word_to_integer(word_to_convert))


def toWordSet(stringlist: list) -> set:
    """Helper function to convert the given stringlist 
    to a set of words."""
    return set(" ".join(stringlist).split())


def toNumberSet(stringlist: list) -> set:
    """Helper function to conver the given stringlist 
    to a set of numbers (converted from words) in string 
    format.
    Currently not used"""
    wordset = toWordSet(stringlist)
    numberList = set()
    for i in wordset:
        numberList.add(word_to_integer(i))
    return numberList


def toNumberStringList(stringlist: list) -> list:
    """Convert the given stringlist to int format.
    Examples:
    ['import socket', 'import numpy'] -> ['123 456','123 789']
    Where '123', '456', '789' varies when algorithm changes"""
    return [
        (lambda x: " ".join(list(map(word_to_integer_string, x.split(" ")))))(i)
        for i in stringlist
    ]


def toNumricalDFA(dfa: dict, counterDict: dict) -> tuple[dict, dict]:
    """This function converts the word in DFA key into 
    integer for miniwizpl to run."""
    numericDFA = {}
    numericCounterDict = {}
    for (state, word), nextState in dfa.items():
        numericDFA[(state, int(word))] = nextState
    for (state, word), nextState in counterDict.items():
        numericCounterDict[(state, int(word))] = counterDict[(state, word)]
    return (numericDFA, numericCounterDict)


def defaultState(stringlist: list) -> tuple:
    """
    Given the string list, returns the default states
    (which has the length of stringlist) with all 0s.
    """
    return tuple(len(stringlist) * [0])


def validDFA(dfa: dict, queue: set, stringlist: list = None, wordset: set = None):
    """ Validate the dfa, update what to be implemented.
    
        A valid dfa is defined to be a dfa that reaches every other states given a
    state, aka strongly connected.
        This function updates the given queue if some states are not implemented,
    and will return True if the dfa is strongly connected.

    Args:
        dfa (dict): the dfa dictionary. \n
        queue (set): a queue that stores what to be implemented next.   \n
        stringlist (list, optional): The target string list. Defaults to None. \n  
        wordset (set, optional): . Defaults to None.    
        
        Note: One of stringlist/wordset must be passed in into the function.

    Returns:
        bool: True/False
    """
    # print(f"\n calling function validDFA(), queue: {queue}")
    states = set(
        [i[0] for i in dfa.keys()] + [i[1] for i in dfa.items()]
    )  # TODO: fix this
    # process if get a stringlist, else use wordset
    if wordset is None:
        try:
            # print("stringlist:",stringlist)
            wordset = toWordSet(stringlist)
        except:
            raise KeyError("must give wordset:set or stringlist:list for reference")

    # print("\t dfa:",dfa)
    # print("\t wordset:",wordset)

    class Graph:
        # Constructor
        def __init__(self, dfa: dict, states: set):
            # A list of lists to represent an adjacency list

            self.adjList = {state: set() for state in states}

            # add edges to the directed graph
            for (src, _), dest in dfa.items():
                # print("add edges to the directed graph", src)
                self.adjList[src].add(
                    dest
                )  # we can do this becasue the dest is where the src can reach through some words

        def __repr__(self) -> str:
            return str(self.adjList)

    # build adjList from dfa
    graph = Graph(dfa=dfa, states=states)

    # print("## Graph made ##")
    # print("\t graph:", graph)
    def DFS(graph: Graph, v: tuple, visited: dict):
        # mark current node as visited
        # print(visited)
        visited[v] = True
        # print("mark current node as visited 'ok'")
        # do for every edge (v, u)
        for u in graph.adjList[v]:
            # `u` is not visited
            if u not in visited:
                visited[u] = False
            else:
                if not visited[u]:
                    DFS(graph, u, visited)

    for initialState in states:
        # run dfs on the initial state, if the dfs reaches the end, meaning that the graph is fully connected
        # visited: keep track of whether a vertex is visited or not
        visited = {state: False for state in states}
        # print(f"in DFS -> visited: {visited}, Graph: {graph}, initial state: {initialState} ")
        DFS(graph, initialState, visited)
        # print("dfs done")
        for word in wordset:
            if (initialState, word) not in dfa:
                queue.add(initialState)  # add the missing item to the queue
                visited[initialState] = False  # will not add new items to visited
            else:
                for nextWord in wordset:
                    if (
                        dfa[(initialState, word)],
                        nextWord,
                    ) not in dfa:  # if the next state is not complete, go to this condition
                        queue.add(dfa[(initialState, word)])  # ((1, 0), 'hello')
                        # visited[initialState] = False # will add new items to visited
                        pass

        # print(f"\t initial state: {initialState}, visited: {visited} " )
        for state in visited:
            if not visited[state]:
                queue.add(state)  # 0,1
                return False
    return True


def assign(
    dfa: dict, stringlist: list, state_to_implement: tuple, word: str, counterDict: dict
):
    """assign one word to its next state"""
    # print("calling function assign()")

    if (state_to_implement, word) in dfa:
        return

    # (current state, word) is not in dfa, need to find the next state
    nextState = list(defaultState(stringlist))  # default state is 0,0
    counterList = [0 for i in stringlist]
    for index in range(len(stringlist)):
        # find which string contains that word
        elements = stringlist[index].split(" ")
        try:
            position = elements.index(word)
            # print(f"{elements} try success with {state_to_implement}, {word}, position: {position}")
        except:
            # word not in this element, state[index] back to 0
            # nextState[index] = 0
            continue  # break out of this iteration

        if (
            position == state_to_implement[index]
        ):  # make sure word is the next word in the string (state); 
            # e.g. ['hi', 'peace'] try success with (1, 1), peace, position: 1
            
            nextState[index] = (
                state_to_implement[index] + 1
            )  # increment the number at state[index]
            if position == len(elements) - 1:
                # reach to the end, increment counter
                counterList[index] += 1
                nextState[index] = 0  # take back to default state
                continue
        elif position == 0:
            # take state[index] to 1
            nextState[index] = 1
    dfa[tuple(state_to_implement), word] = tuple(nextState)
    counterDict[tuple(state_to_implement), word] = counterList
    # print(f"\t ({state_to_implement}, {word}) -> nextState: {nextState}, counterList: {counterList} \n")


def eliminateRedundency(dfa: dict, counterDict: dict, stringlist: list) -> tuple[dict, dict]:
    """
        This function should be called after the whole dfa has been made and validated.
        This function will return a copy to the given dfa, which have all the redundent
    states iliminated.

    Args:
        dfa (dict): a complete dfa
    """
    newdfa = dfa.copy()
    newCounterDict = counterDict.copy()
    for key in dfa.keys():
        if dfa[key] == defaultState(stringlist) and counterDict[key] == list(defaultState(stringlist)):
            del newdfa[key]
        #if counterDict[key] == list(defaultState(stringlist)):
            del newCounterDict[key]

    #print(f"DFA: {newdfa}, counterDict: {counterDict}")
    return (newdfa, newCounterDict)


def __dfa_from_string_full(stringlist: list[str]) -> tuple[dict, dict]:
    """
        This function builds the dfa from a list of strings.
        This function is made to be private because it does not update the
        global variable counterDict from global_vars.py.

    Args:
        stringlist (list[str]): A python list of strings (grouped by sentences)
                                to be find in the document

    Returns:
        tuple[dict, dict]
    """

    wordset: set = toWordSet(stringlist)
    # print(stringlist)
    # print(wordset)
    queue = set()
    dfa = {}
    counterDict = {}
    assign(
        dfa=dfa,
        stringlist=stringlist,
        state_to_implement=defaultState(stringlist),
        word=list(wordset)[0],
        counterDict=counterDict,
    )

    while not validDFA(dfa, queue=queue, wordset=wordset):
        # every state should have somewhere to go, the graph is the dfa, the node is the state
        for state_to_implement in queue:
            for word in wordset:
                assign(dfa, stringlist, state_to_implement, word, counterDict)

    return (dfa, counterDict)


def dfa_from_string(stringlist: list[str], test=False) -> dict:
    """
        This function builds the dfa from a list of strings, the same logic 
        with dfa_from_string_full, except it would eliminate redunency of 
        the DFA & counterDict. This function will also update the global 
        variable counterDict and counterList as needed. The global variables
        will not be returned.

    Args:
        stringlist (list[str]): A python list of strings (grouped by sentences)
                                to be find in the document
        test (bool): A boolean variable to specify if we are testing. If test is True,
                     the dfa will have the actual words in the dfa; else the returned
                     dfa will use calculated integers for the words.
    Returns:
        dfa: dict
    """
    if test:
        # If test is specified, we are using the actual words instead of the numbers,
        # which allows miniwizpl to process.
        (dfa, counter_dict) = __dfa_from_string_full(stringlist=stringlist)
        (dfa, counter_dict) = eliminateRedundency(dfa, counter_dict, stringlist)
    else:
        stringlist = toNumberStringList(stringlist)
        (dfa, counter_dict) = __dfa_from_string_full(stringlist=stringlist)
        (dfa, counter_dict) = eliminateRedundency(dfa, counter_dict, stringlist)
        (dfa, counter_dict) = toNumricalDFA(dfa, counter_dict)
    print("stringlist: ",stringlist)
    print(f"DFA: {dfa}, counterDict: {counter_dict}")
    global counterDict # init counterDict and counterList as global vars. According to tests, these variables cannot be declared outside, otherwise they will be in different memory address when reassigned with new values.
    counterDict = counter_dict
    global counterList
    counterList = [0 for i in range(len(stringlist))]
    print(f"!!! assigning counterDict: {counterDict, id(counterDict)}, counterList: {counterList, id(counterList)}")
    return dfa  # since we updated the global variable counterDict in the line before, returning two values is not necessary.


def incrementCounterList(state):
    """
    This function takes in a state, increament the counter based on the counterDict.
    Cannot be called in the mux() funciton, because it runs everytime the mux() is called.

    Args:
        state (tuple): a state within the dfa, with format tuple(tuple, word)
    """
    global counterDict
    global counterList
    if state in counterDict:
        toIncrement = counterDict[state]
        for i in range(len(counterList)):
            counterList[i] += toIncrement[i]
        print(f"Updating counterList: {counterList}, counterDict: {counterDict[state]}")
    return 
    # return next_state # need to return becuase used in mux()


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

    def next_state_fun(word, initial_state): # TODO: initial_state could be a tuple?? try this out
        '''
            I changed this part, otherwise when two sub texts are not contonious,
            the DFA never moves from the zero state
        '''
        # go to zeroState always, unless we have the next state in the DFA
        curr_state = zeroState 
        for (dfa_state, dfa_word), next_state in dfa.items():
            #print(
                # "curr state: ", val_of(curr_state),"\n",
                # "dfa state: ", dfa_state, "\n", initial_state == stateCal(dfa_state),
                # "input string: ", val_of(word),
                # "dfa string: ", dfa_word, "\n",val_of(word) == dfa_word ,
                # "next_state", next_state)
            
            # transform all tuples to numbers
            stateCal_state = stateCal(dfa_state) 
            stateCal_next = stateCal(next_state)
            curr_state = mux((initial_state == stateCal_state) & (word == dfa_word),
                             stateCal_next,
                             curr_state)
            # unused, we should not reveal the value of the multiplexer
            # question = mux((initial_state == stateCal_state) & (word == dfa_word),
            #                  #stateCal_next,
            #                  True,
            #                  False)
            # if val_of(question):
            #     incrementCounterList(state=(dfa_state,dfa_word))
            
            global counterList
            global counterDict
            length = len(dfa_state)
            vec = [counterList[i] + counterDict[(dfa_state,dfa_word)][i] for i in range(length)] # !!! counterList must be hidden, ask if we can add Secret list to a public list.
                
            counterList = mux((initial_state == stateCal_state) & (word == dfa_word),
                              vec,
                              counterList)

        # print(f"initial state: {val_of(initial_state)}, curr_state: {val_of(curr_state)}, word: {val_of(word)}")
        # print(f"dfa_state: {dfa_state}, stateCal_state: {stateCal_state}, next state: {next_state}")
        # print()
        
        # return curr_state since we are using reduce() for the loop
        return curr_state

    reduce(next_state_fun, document, zeroState)
    
    # cleanup
    global counterList 
    global counterDict
    
    local_counterList = counterList.copy()
    return local_counterList
