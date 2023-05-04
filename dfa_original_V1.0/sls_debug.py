import sys
from miniwizpl import *
from miniwizpl.expr import *

sys.path.append("/usr/src/app/examples/substring_search/common")
from util import *


def islast(idx, sub_txt):
    '''
        This function checks whether or not the current index reached the last idx of the sub_txt
        Meaning, to check whether or not there is any uncovered element in the sub text
    '''
    if len(sub_txt.split()) - 1 == idx:
        return True
    else:
        return False


def equals(curr_state, pivot_state):
    '''
        This function compares the current state and pivot_state
        If different, i.e., something new is derived from the pivot_state,
        then the new state will be added to the states list
    '''
    for i in range(len(curr_state)):
        if curr_state[i] != pivot_state[i]:
            return False

    return True


def stateCal(s):
    result = 0
    for i in range(len(s)):
        result += (s[i] << 8 * i)
    return result

def state_index(state, index):
    # print(val_of((state >> 8*index) & 255), val_of(state) >> 8*index & 255)
    # print(type(state), type(8*index))
    return (state >> 8*index) & 255

def overwrite_with_accept(accept_state, curr_state, index):
    # print(type(curr_state), type(accept_state))
    return curr_state | (accept_state << (8* index))

def dfa_from_string(stringlist, accept_state):
    length = len(stringlist)
    pointer = [0] * length
    next_state = {}
    wordlist = set(' '.join(stringlist).split())
    states = [pointer]  # keep track of all states
    count = 0
    finished = False  # not all accepted
    while not finished:
        state = states[count]
        counter = len(states)
        for word in wordlist:
            pointer = state.copy()
            for i in range(length):  # 0,1,2
                if state[i] != accept_state:
                    if word == stringlist[i].split()[state[i]]:
                        if islast(state[i], stringlist[i]):
                            pointer[i] = accept_state
                        else:
                            pointer[i] += 1
                    else:
                        pointer[i] = 0
            if not equals(pointer, state):
                states.append(pointer)
                next_state[tuple(state), word_to_integer(word)] = tuple(pointer)
        if counter < len(states):
            count += 1
        else:
            finished = True
    return next_state


def run_dfa(dfa, string, zero_state, accept, stateLength):
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

            # curr_state = mux((initial_state == dfa_state) & (word == dfa_word),
            #              next_state,
            #              mux((initial_state == dfa_state) & (word != dfa_word) & (initial_state!=zero_state),
            #              error_state,
            #              curr_state))  # output here is a number, not a tuple

            # print("Updated state: ", val_of(curr_state))

            # TODO: check if output has any accept state for a single string: need to use the reverse version of
            #  stateCal()
            # TODO: if any accept state, actual_counter[index]++ and change the state back to 0
        for i in range(stateLength):
            print("value of index",i,": ", state_index(initial_state, i))
            curr_state = mux(state_index(initial_state,i) == 255,
                            overwrite_with_accept(255, curr_state,i),
                            curr_state)  # TODO: this line might need to be changed for the counter.
            print("curr_state: ", val_of(curr_state))
        print("initial state: ", val_of(initial_state), "current state: ", val_of(curr_state), "\n")
        return curr_state

    latest_state = reduce(next_state_fun, string, zero_state)
    return latest_state


def main(target_dir, prime, prime_name, size, operation):
    # Importing ENV Var & Checking if prime meets our requirement

    assert len(sys.argv) == 6, "Invalid arguments"
    _, target_dir, prime, prime_name, size, operation = sys.argv
    file_name = "stringlist_search"
    set_field(int(prime))

    try:
        assert check_prime() == True
    except:
        print("no equivalent prime (2305843009213693951) in ccc.txt")
        sys.exit(1)

    # Prepping target text and substrings

    if operation == "test":
        corpus = generate_text(int(size))
        string_target = generate_target(corpus, file_name, length=2, n_string=4)
        print("Test (First 10 Strings): ", corpus[0:10])
        print("Actual text length:", len(corpus))

    else:
        string_target = ['one two', 'three five']

        with open("/usr/src/app/examples/dfa_test_input.txt", 'r') as f:
            corpus = f.read()
        corpus = corpus.split()
        print("Text: ", corpus, "\n")

    print("Target: ", string_target, "\n")

    # Transform the text file to search into miniwizpl format

    file_string = SecretList([word_to_integer(_str) for _str in corpus])

    accept_state = 255
    accept = tuple([255] * len(string_target))
    accept = stateCal(accept)
    zero_state = tuple([0] * len(string_target))
    zero_state = stateCal(zero_state)
    error_state = 1000

    # TODO: a reverse version of stateCal() to transform a number back to a state tuple.
    # TODO: actual_counter = [0,0,0,...]
    # TODO: expected_counter = [1,2,3,...]

    # Build and traverse a DFA

    dfa = dfa_from_string(string_target, accept_state)
    # print("\n", "DFA: ",dfa, "\n")
    print("Traversing DFA")
    stateLength = len(string_target)
    latest_state = run_dfa(dfa, file_string, zero_state, accept, stateLength)
    print("Output Assertion")
    assert0(latest_state - accept)
    print("Running Poseidon Hash")
    run_poseidon_hash(file_string)
    print("\n", "Latest State: ", val_of(latest_state), "\n")

    # TODO: instead of comparing the run_dfa result, we will need to compare the actual_counter with the expected_counter.

    print('accept ', accept)
    print('accept_state ', accept_state)

    if val_of(latest_state) == accept:
        print("DFA successfully reached the accept state \n")
    else:
        print("DFA did not reached the accept state \n")

    print("Generating Output \n")
    print_ir0(target_dir + "/" + f"{file_name}_{prime_name}_{size}")


if __name__ == '__main__':
    main(*sys.argv[1:])