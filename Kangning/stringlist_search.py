import sys
import functools
import hashlib
from miniwizpl import SecretInt, SecretList, mux, public_foreach, print_emp

if len(sys.argv) != 2:
    print("Usage: python dfa_example.py <target_filename>")
    sys.exit()


def word_to_integer(word):
    hash = hashlib.sha256(word.encode('utf-8')).digest()
    hash = int.from_bytes(hash, 'big')
    hash = hash >> 8 * 28 + 1
    return hash


accept_state = 255


def islast(i, word):
    if len(word.split()) - 1 == i:
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

with open(sys.argv[1], 'r') as f:
    file_data = f.read()

file_data = file_data.split()
file_string = SecretList([word_to_integer(c) for c in file_data])
counter = SecretList()
dfa = dfa_from_string(strings_present)


# The helper function for comparing two state values
def stateCal(s):
    result = 0
    for i in range(len(s)):
        result += (s[i] << 8 * i)
    return result



# TODO: a reverse version of stateCal() to transform a number back to a state tuple.

accept = tuple([255] * len(strings_present))
accept = stateCal(accept)
zero_state = tuple([0] * len(strings_present))
zero_state = stateCal(zero_state)


# TODO: actual_counter = [0,0,0,...]
# TODO: expected_counter = [1,2,3,...]

def run_dfa(dfa, string):
    def next_state_fun(word, state):
        output = zero_state

        for (dfa_state, dfa_word), next_state in dfa.items():
            # transform all tuples to numbers
            dfa_state = stateCal(dfa_state)
            next_state = stateCal(next_state)
            output = mux((state == dfa_state) & (word == dfa_word),
                         next_state,
                         output)  # output here is a number, not a tuple
            # TODO: check if output has any accept state for a single string: need to use the reverse version of
            #  stateCal()
            #hello world + world peace
            #((0,0),hello):hello -> ((1,0),world):world -> ((acc,1), peace):peace -> ((acc,acc),):
            #                                           -> ((0,1),peace):peace  -> ((0,acc), hello)
            # TODO: if any accept state, actual_counter[index]++ and change the state back to 0
        output = mux(state == accept, accept, output)  # TODO: this line might need to be changed for the counter.

        return output

    return public_foreach(string,
                          next_state_fun,
                          zero_state)


'''
def public_foreach(ls, fn, init):
    accumulator = init
    for x in ls:
        accumulator = fn(x, accumulator)
    return accumulator
'''

# define the ZK statement


outputs = (run_dfa(dfa, file_string) == accept)
# TODO: instead of comparing the run_dfa result, we will need to compare the actual_counter with the expected_counter.
print(outputs)

# compile the ZK statement to an EMP file

# output = functools.reduce(lambda a, b: a & b, outputs)
print_emp(outputs, 'miniwizpl_test.cpp')
