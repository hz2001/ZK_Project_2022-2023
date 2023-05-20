# author: Herbert Zhang
# Date: 10/13/2022
# The second draft of this project, currently not used, because could not integret with miniwizpl environment, and the algorithm is buggy with many edge cases.

import sys
from miniwizpl import SecretInt, SecretList, mux, public_foreach, print_emp, assert0
from miniwizpl.expr import *
import timeit

# whitelist = ["import numpy", "import socket", "import hello import world import world import", "something"]  # buggy

whitelist = ["hello world", "hello mini", "import socket", "import mini hello"]


###############################
### Before Using secretList ###
###############################


def word_to_integer(word):
    hash = 0
    for i in range(len(word)):
        hash += (ord(word[i]) << 8 * i)
    return hash


def hash_list(lst: list) -> list:
    list_result = []
    for i in whitelist:
        elements = ""
        for word in i.split(" "):
            key = word_to_integer(word)
            elements += " " + str(key)
        list_result.append(elements[1:])
    return list_result



def parse_list(lst):
    alphabet = {}
    for words in lst:
        elements = words.split(" ")
        previous = None
        for word in elements:
            try:
                word = int(word)
            except:
                print("detected a non integer element in the list")
            if word not in alphabet:
                # TODO: change the structure of the alphabet to [counter, [next states], [current_state]]
                alphabet[word] = [1, [], []]  # (state number, how many presented, what words follows it)
            else:
                alphabet[word][0] += 1
            if previous is not None:
                if word not in alphabet[previous][1]:
                    alphabet[previous][1].append(word)
            previous = word
    # the above code assumes that string "else" is not in our input document,
    # and we will replace all words which are not in our list to "else" keyword.
    alphabet[word_to_integer('else')] = [1, [], []]
    # if an accept state is achieved, then one string in the list is found
    accept_states = {int(words.split(" ")[-1]): True for words in lst}
    # check if any words in the accept states has following word in alphabet, if so, this means that this word serves as
    zero_states = [int(words.split(" ")[0]) for words in lst]
    return alphabet, accept_states, zero_states


# def build_states(alphabet, zeroStates: list) -> dict:
#     result = {word: (alphabet[word][0], alphabet[word][1]) for word in alphabet.keys()}
#     return result


# TODO: test code
args = sys.argv[1:]
if len(args) != 1:
    print("argument length not correct")
elif type(args[0]) is not str:
    print("argument must have a file name string")
else:
    with open(args[0], mode="r") as file:
        file_data = file.read().split()
    file.close()
    hashed_list = hash_list(whitelist)
    states, a_states, z_states = parse_list(hashed_list)
    print(a_states)
    print("zero_states:", z_states)
    print("state diagram:", states)
    init = states[word_to_integer('else')]

###############################
### AFTER Using secretList ####
###############################

file_string = SecretList([word_to_integer(c) for c in file_data])
secret_while_list = SecretList(hashed_list)

# TODO: reinstall miniwizpl
def public_foreach(xs, f, init, additional_args):
    # additional_args should be a secret list/ regular list
    assert isinstance(xs, SecretList)
    t_a = type(init)

    # TODO: how can we handle the values here?
    x = SymVar(gensym('x'), SecretInt, None)
    a = SymVar(gensym('a'), t_a, None)
    r = f(x, a, additional_args)

    # compute the actual result
    a_val = val_of(init)
    for x_val in val_of(xs):
        a_val = val_of(f(x_val, a_val, additional_args))
    # TODO: the function f must contain a method to form the corresponding secret type of additional_args
    loop = Prim('fold', [x, r, a, xs, init], a_val)
    return loop


def assert_acc(states, required_counts):
    # TODO: required counts
    for (cnt, nexts) in states.items():
        output = mux(cnt <= 0, True, False)
        if not output:
            return False
    return True


'''
If in next_state:
    if accept: 
        if current string in list: decrement, []
        else: []
    elif init: [word]
    elif regular: += [word]
else:
    if init: [word]
    else: []

If the current substring (word) is in next_states, and is an init state, (can we ignore that it is a init state? no) then _current += [word]
                                is not in next_states, and is an init state, _current -> [word]
If the current substring (word) is in next_states, and is a regular state, then current_string += word
If the current substring (word) is in next_states, and is a accept state, then     current_string -> [] decrement
                                is not in next_states, and is regular/accept state, _current -> []
'''
# the DFA can contain every information, including current_string field and the init_states/accept_states information
# TODO:do more testing to ensure the result is correct
def run_dfa(doc: str, dfa: dict) -> dict:
    def next_state_fun(word, current_state, current_string:list, lst:list):
        result = init
        (count, nexts) = dfa[current_state]
        if word in nexts:
            if word in a_states:
                # check if the current string presents in the list
                current_string.append(word)
                if current_string in lst:
                    for i in current_string:
                        dfa[i][0] -= 1
                current_string = []
            elif word in init:
                current_string = [word]
                result = word
            else:
                current_string.append(word)
                result = word
        else:
            current_string = []
            if word in init:
                current_string.append(word)
                result = word

        return result, current_string, lst
        # TODO: mux

    return public_foreach(doc,
                          next_state_fun,
                          init)


startTime = timeit.timeit()
# run_dfa(file_string, states)
# outputs = mux(assert_acc(states), True, False)

# print_emp(outputs, 'miniwizpl_test.cpp')
endTime = timeit.timeit()
print(startTime - endTime)
