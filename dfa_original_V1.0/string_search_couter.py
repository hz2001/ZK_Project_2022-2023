import sys
import functools
import hashlib
from miniwizpl import SecretInt, SecretList, mux, public_foreach, print_emp
from miniwizpl.expr import *

sys.path.append("./common")
from common.util import *


def word_to_integer(word):
    hash = hashlib.sha256(word.encode('utf-8')).digest()
    hash = int.from_bytes(hash, 'big')
    hash = hash >> 8 * 28 + 1
    return hash


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


# The helper function for comparing two state values
def stateCal(s):
    result = 0
    for i in range(len(s)):
        result += (s[i] << 8 * i)
    return result


# def run_dfa(dfa, string):
#     def next_state_fun(word, state):
#         output = zero_state
#
#         for (dfa_state, dfa_word), next_state in dfa.items():
#             # transform all tuples to numbers
#             dfa_state = stateCal(dfa_state)
#             next_state = stateCal(next_state)
#             output = mux((state == dfa_state) & (word == dfa_word),
#                          next_state,
#                          output)  # output here is a number, not a tuple
#             # TODO: check if output has any accept state for a single string: need to use the reverse version of
#             #  stateCal()
#             # TODO: if any accept state, actual_counter[index]++ and change the state back to 0
#         output = mux(state == accept, accept, output)  # TODO: this line might need to be changed for the counter.
#
#         return output
#
#     return public_foreach(string,
#                           next_state_fun,
#                           zero_state)


def run_dfa(dfa, string, zero_state, accept):
    def next_state_fun(word, initial_state):
        curr_state = initial_state

        for (dfa_state, dfa_word), next_state in dfa.items():
            dfa_state = stateCal(dfa_state)
            next_state = stateCal(next_state)

            curr_state = mux((initial_state == dfa_state) & (word == dfa_word),
                             next_state,
                             curr_state)

        curr_state = mux(initial_state == accept, accept,
                         curr_state)  # TODO: this line might need to be changed for the counter.

        return curr_state

    latest_state = reduce(next_state_fun, string, zero_state)
    return latest_state


'''
def public_foreach(ls, fn, init):
    accumulator = init
    for x in ls:
        accumulator = fn(x, accumulator)
    return accumulator
'''


# define the ZK statement


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
    latest_state = run_dfa(dfa, file_string, zero_state, accept)
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

# if len(sys.argv) != 2:
#     print("Usage: python dfa_example.py <target_filename>")
#     sys.exit()
# accept_state = 255
# strings_present = [
#     'import socket',
#     'import numpy',
#     'hello world',
#     'import sys'
# ]
#
# strings_not_present = [
#     'import socket'
# ]
#
# with open(sys.argv[1], 'r') as f:
#     file_data = f.read()
#
# file_data = file_data.split()
# file_string = SecretList([word_to_integer(c) for c in file_data])
#
# dfa = dfa_from_string(strings_present)


# accept = tuple([255] * len(strings_present))
# accept = stateCal(accept)
# zero_state = tuple([0] * len(strings_present))
# zero_state = stateCal(zero_state)
# outputs = (run_dfa(dfa, file_string) == accept)
# # TODO: instead of comparing the run_dfa result, we will need to compare the actual_counter with the expected_counter.
# print(outputs)
#
# # compile the ZK statement to an EMP file
#
# # output = functools.reduce(lambda a, b: a & b, outputs)
# print_emp(outputs, 'miniwizpl_test.cpp')
# # TODO: a reverse version of stateCal() to transform a number back to a state tuple.
# # TODO: actual_counter = [0,0,0,...]
# # TODO: expected_counter = [1,2,3,...]
