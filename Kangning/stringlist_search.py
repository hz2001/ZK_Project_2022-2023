import pprint
import random
import sys
import functools
from miniwizpl import SecretInt, SecretList, mux, public_foreach, print_emp

if len(sys.argv) != 2:
    print("Usage: python dfa_example.py <target_filename>")
    sys.exit()

# the accept state is 1000000
accept_state = 1000000


def word_to_integer(word):
    hash = 0

    for i in range(len(word)):
        hash += (ord(word[i]) << 8 * i)

    return hash


# a Python function to create a dfa from a string
# we assume a default transition back to 0
def islast(i, word):
    if len(word) - 1 == i:
        return True
    else:
        return False


def equals(pointer, state):
    for i in range(len(pointer)):
        if pointer[i] != state[i]:
            return False
    return True


def dfa_from_string(stringlist):
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


strings_present = [
    'import socket',
    'import numpy',
    'hello world',
    'import sys'
]

strings_not_present = [
    'import socket'
]

# read the target file & convert to secret string
with open(sys.argv[1], 'r') as f:
    file_data = f.read()

file_data = file_data.split()
file_string = SecretList([word_to_integer(c) for c in file_data])


# run a dfa
def run_dfa(dfa, string, len):
    def next_state_fun(word, state):
        output = [0]*len
        accept_state_final = tuple([accept_state]*len)
        for (dfa_state, dfa_word), next_state in dfa.items():
            output = mux((state == dfa_state) & (word == dfa_word),  # can compare tuples?
                         next_state,
                         output)

        output = mux(state == accept_state_final, accept_state_final, output)
        return output

    return public_foreach(string,
                          next_state_fun,
                          0)


# define the ZK statement
outputs = []

dfa = dfa_from_string(strings_present)
outputs.append(run_dfa(dfa, file_string, len(strings_present)) == accept_state)
# will output accept when all is found


dfa = dfa_from_string(strings_not_present) # maybe not
outputs.append(run_dfa(dfa, file_string) != accept_state)

print(outputs)
# compile the ZK statement to an EMP file
output = functools.reduce(lambda a, b: a & b, outputs)
print_emp(output, 'miniwizpl_test.cpp')
