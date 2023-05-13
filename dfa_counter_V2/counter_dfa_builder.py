# Author: Herbert Zhang
# This file contains everything that we need to build the dfa with counter.

from .util import *

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

def toWordSet(stringlist: list) -> set:
    """ Helper function to convert the given stringlist to a set of words"""
    return set(' '.join(stringlist).split())

def toNumberSet(wordset: set) -> set:
    newset = set()
    for i in wordset:
        newset.add(word_to_integer(i))
    return newset

def defaultState(stringlist: list) -> tuple:
    """
    Given the string list, return the default states 
    (which has the length of stringlist) with all 0s.
    """
    return tuple(len(stringlist)*[0])

def validDFA(dfa:dict, queue: set, stringlist: list = None, wordset: set = None):
    """
        A valid dfa is defined to be a dfa that reaches every other states given a 
    state, aka strongly connected.
        This function will update the given queue if some states are not implemented,
    and will return True if the dfa is strongly connected.

    Args:
        dfa (dict): the dfa dictionary.
        queue (set): a queue that stores what to be implemented next.
        stringlist (list, optional): _description_. Defaults to None.
        wordset (set, optional): _description_. Defaults to None.

    Returns:
        bool: True/False
    """
    # print(f"\n calling function validDFA(), queue: {queue}")
    states = set([i[0] for i in dfa.keys()]+[i[1] for i in dfa.items()]) # TODO: fix this 
    # process if get a stringlist, else use wordset
    if wordset is None:
        try:
            # print("stringlist:",stringlist)
            wordset = toWordSet(stringlist)
            wordset = toNumberSet(wordset)
        except:
            raise KeyError("must give wordset:set or stringlist:list for reference")
        
    # print("\t dfa:",dfa)
    # print("\t wordset:",wordset)
    
    class Graph:
        # Constructor
        def __init__(self, dfa: dict, states: set):
            # A list of lists to represent an adjacency list

            self.adjList = {state:set() for state in states}

            # add edges to the directed graph
            for ((src, _), dest) in dfa.items():
                # print("add edges to the directed graph", src)
                self.adjList[src].add(dest) # we can do this becasue the dest is where the src can reach through some words, we just care about 
        def __repr__(self) -> str:
            return str(self.adjList)

    # build adjList from dfa
    graph = Graph(dfa = dfa, states=states)
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
        visited = {state:False for state in states}
        # print(f"in DFS -> visited: {visited}, Graph: {graph}, initial state: {initialState} ")
        DFS(graph, initialState, visited)
        # print("dfs done")
        for word in wordset:
            if (initialState, word) not in dfa:
                queue.add(initialState) # add the missing item to the queue
                visited[initialState] = False # will not add new items to visited
            else:
                for nextWord in wordset:
                    if (dfa[(initialState, word)], nextWord) not in dfa: # if the next state is not complete, go to this condition
                        queue.add(dfa[(initialState, word)]) # ((1, 0), 'hello')
                        # visited[initialState] = False # will add new items to visited
                        pass

        print(f"\t initial state: {initialState}, visited: {visited} " )
        for state in visited:
            if not visited[state]:
                queue.add(state) # 0,1
                return False
    return True

def assign(dfa: dict, stringlist: list, state_to_implement:tuple, word:str, counterDict:dict):
    """ assign one word to its next state
    """
    # print("calling function assign()")

    if (state_to_implement, word) in dfa:
        return

    # (current state, word) is not in dfa, need to find the next state
    nextState = list(defaultState(stringlist)) # default state is 0,0
    counterList= [0 for i in stringlist]
    for index in range(len(stringlist)):
        # find which string contains that word
        elements = stringlist[index].split(" ")
        try:
            position = elements.index(word)
            # print(f"{elements} try success with {state_to_implement}, {word}, position: {position}")
        except:
            # word not in this element, state[index] back to 0
            # nextState[index] = 0
            continue # break out of this iteration

        if position == state_to_implement[index]: # make sure word is the next word in the string (state); e.g. ['hi', 'peace'] try success with (1, 1), peace, position: 1
            nextState[index] = state_to_implement[index] + 1 # increment the number at state[index]
            if position == len(elements) -1:
                # reach to the end, increment counter
                counterList[index] += 1
                nextState[index] = 0 # take back to default state
                continue
        elif position == 0:
            # take state[index] to 1
            nextState[index] = 1
    dfa[tuple(state_to_implement), word] = tuple(nextState)
    counterDict[tuple(state_to_implement), word] = counterList
    # print(f"\t ({state_to_implement}, {word}) -> nextState: {nextState}, counterList: {counterList} \n")

def eliminateRedundency(dfa: dict, counterDict: dict, stringlist: list) -> tuple:
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
            del newCounterDict[key]
    
    print(f"DFA: {newdfa}, counterDict: {counterDict}")
    return (newdfa, newCounterDict)

def dfa_from_string_full(stringlist: list[str]) -> tuple[dict, dict]:
    """
        This function builds the dfa from a list of strings.

    Args:
        stringlist (list[str]): A python list of strings (grouped by sentences)
                                to be find in the document

    Returns:
        tuple[dict, list]
    """
    wordset: set = toNumberSet(toWordSet(stringlist))
    queue = set()
    dfa = {}
    counterDict = {}
    assign(dfa = dfa,
           stringlist= stringlist,
           state_to_implement= defaultState(stringlist),
           word = list(wordset)[0],
           counterDict = counterDict)

    while not validDFA(dfa, queue = queue, wordset = wordset):
        # every state should have somewhere to go, the graph is the dfa, the node is the state
        for state_to_implement in queue:
            for word in wordset:
                assign(dfa, stringlist, state_to_implement, word, counterDict)
    
    return (dfa, counterDict)

def dfa_from_string(stringlist: list[str]) -> tuple[dict, dict]:
    """
            This function builds the dfa from a list of strings, the same logic with dfa_from_string_full,
        except it would eliminate redunency of the DFA & counterDict.

    Args:
        stringlist (list[str]): A python list of strings (grouped by sentences)
                                to be find in the document

    Returns:
        tuple[dict, list]
    """
    (dfa, counterDict) = dfa_from_string_full(stringlist = stringlist)
    return eliminateRedundency(dfa, counterDict, stringlist)
