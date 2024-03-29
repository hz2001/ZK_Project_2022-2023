# author: Herbert Zhang
# Date: 11/13/2022
# The third draft of this project, currently not used, because could not integret with miniwizpl environment, and the algorithm is buggy with many edge cases.

import sys
from miniwizpl import SecretInt, SecretList, mux, public_foreach, print_emp, assert0
import timeit

whitelist = ["import numpy", "import socket", "import hello import world import world import", "something"]  # buggy


# whitelist = ["hello world hello world numpy", "hello mini hello mini hello"]

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
    word_to_init = {}
    for i in whitelist:
        elements = ""
        for word in i.split(" "):
            key = word_to_integer(word)
            # print(word, key)
            elements += " " + str(key)
            if key not in word_to_init:
                word_to_init[key] = word_to_integer(word + "_init")
        list_result.append(elements[1:])
    # print(list_result)
    # print(word_to_init)
    return list_result, word_to_init


def parse_list(lst: list) -> dict:
    alphabet = {}
    for words in lst:
        elements = words.split(" ")
        previous = None
        for word in elements:
            word = int(word)
            if word not in alphabet:
                alphabet[word] = [word, 1, []]  # (state number, how many presented, what words follows it)
            else:
                alphabet[word][1] += 1
            if previous is not None:
                if alphabet[word][0] not in alphabet[previous][2]:
                    alphabet[previous][2].append(alphabet[word][0])
            previous = word
    # the above code assumes that string "else" is not in our input document,
    # and we will replace all words which are not in our list to "else" keyword.
    alphabet[word_to_integer('else')] = [word_to_integer('else'), 1, []]
    foo, mapping = hash_list(lst=lst)
    # return alphabet
    return update_alphabet(lst, alphabet, mapping)


def update_alphabet(lst, alphabet, mapping):
    # print("alphabet before", alphabet)
    # TODO: remove the redundent code where a word is mapped to the init_ version
    for words in lst:
        elements = words.split(" ")
        if len(elements) > 1:
            for word in elements[1:]:
                word = int(word)
                element1 = elements[1]
                # this element appears as the zero state and regular state
                # we add another element to the alphabet to represent the first occurrence of that element
                if word == elements[0] and mapping[word] not in alphabet:
                    alphabet[mapping[word]] = [largest_id, 1, [alphabet[element1][0]]]
                    alphabet[word][1] -= 1
                    # print(word, alphabet[word][2], alphabet[elements[1]][0])
                    try:
                        alphabet[word][2].remove(alphabet[element1][0])
                    except ValueError:
                        print("value Error ", word, alphabet[word][2], alphabet[element1][0])
                        pass
                    break
                elif word == elements[0] and mapping[word] in alphabet:
                    alphabet[mapping[word]][1] += 1
                    alphabet[word][1] -= 1
                    if alphabet[element1][0] not in alphabet[mapping[word]][2]:
                        alphabet[mapping[word]][2].append(alphabet[elements1][0])
                    break
        else:
            # len(elements) = 1, we ignore it
            pass

    # print("alphabet after", alphabet)
    return alphabet


'''
alphabet = {128034844732777: [128034844732777, 2, [521577264494, 127978942197619]], 521577264494: [521577264494, 1, []], 127978942197619: [127978942197619, 1, []], 478560413032: [478560413032, 2, [431316168567]], 431316168567: [431316168567, 1, [478560413032]], 1907970644657937674099: [19079706446579376740
99, 1, []], 1702063205: [1702063205, 1, []]}

'id as number': [ id, occurrence, [follow ups]]


Ex: states: {0:{counter,1,4}, 1:{counter,1,4,2,3,0}, 2:{counter,0,1,4}, 3:{counter,0,1,4},4:{counter,0,1,4,5},5{counter,0,1}}
'''


# the old version of get zero states method, for reference
def old_get_zero_states(lst, alphabet, mapping):
    # loop through our list and assign each states
    zero_states = {}
    for words in lst:
        elements = words.split(" ")  # ["hello", "world"]
        element0 = int(elements[0])
        element0_map = int(elements[0])
        if mapping[element0] in alphabet:
            zero_states[mapping[element0]][0] = True
        elif alphabet[element0][
            0] not in zero_states:  # elements[0] is the first item, alphabet[elements[0]][0] is word id
            zero_states[alphabet[elements[0]][0]] = True
    return [state for state in zero_states], zero_states  # returns a list and a dic which have the same elements


def get_zero_states(lst, alphabet, mapping):
    # loop through our list and assign each states
    zero_states = {}
    for words in lst:
        elements = words.split(" ")  # ["hello", "world"]
        element0 = int(elements[0])
        element0_map = int(elements[0])
        if mapping[element0] in alphabet:
            zero_states[mapping[element0]][0] = True
        elif alphabet[element0][
            0] not in zero_states:  # elements[0] is the first item, alphabet[elements[0]][0] is word id
            zero_states[alphabet[elements[0]][0]] = True
    return [state for state in zero_states], zero_states  # returns a list and a dic which have the same elements


def get_accept_states(lst, alphabet) -> dict:
    result = {}
    for words in lst:
        elements = words.split(" ")
        if len(elements) != 1:  # if len(element) == 1 then it is a special case where it might be the first
            result[alphabet[elements[-1]][0]] = True
        else:
            result[alphabet[elements[-1]][
                0]] = True  # *maybe need to change* currently we don't care about the instance when there is a word both at accept state and in the unaccept state
    return result


def build_states(lst: list, zeroStates: list) -> dict:
    # lst represent black list or white list
    result = {}
    # initiate the states dictionary
    for word in alphabet:
        word_id = alphabet[word][0]
        # check if the word is accept or not; if yes, add 1 to the beginning, and when encounter it, reduce it to 0
        '''
        states[word_id] = occurrence_counter + next_states + zero_states
        '''
        result[word_id] = [alphabet[word][1]] + alphabet[word][2] + zeroStates
    return result


startTime = timeit.timeit()
# initiate all required fields
args = sys.argv[1:]
if len(args) != 1:
    print("argument length not correct")
elif type(args[0]) is not str:
    print("argument must have a file name string")
else:
    with open(args[0], mode="r") as file:
        file_data = file.read().split()
    file.close()
    hashed_white_list, word_init_list = hash_list(whitelist)
    alphabet = parse_list(hashed_white_list)
    print(alphabet)
    zero_states, zero_dic = get_zero_states(lst=hashed_white_list, alphabet=alphabet, mapping=word_init_list)
    states = build_states(hashed_white_list, zero_states)
    init = states[word_to_integer('else')]
    print(states)

###############################
### AFTER Using secretList ####
###############################

file_string = SecretList([word_to_integer(c) for c in file_data])
print(file_string)
'''
alphabet = {'import': [1, 3, [2,3,6]], 'numpy': [2, 1, []], 'socket': [3, 1, []], 'hello': [4, 1, [5]], 'world': [5, 1, []], 'else': [0, 0, []]}       'import': [word id, occurrence, [follow ups]]
import numpy

Ex: states: {0:{counter,1,4}, 1:{counter,1,4,2,3,0}, 2:{counter,0,1,4}, 3:{counter,0,1,4},4:{counter,0,1,4,5},5{counter,0,1}}
'''


def new_run_dfa(states, doc):
    def next_state_fun(word, state):
        result = init
        for word_id, word_count, words_to_follow in states.items():
            # TODO:

            # TODO: compare the current state dictionary with the acceptance state dictionary
            # (which a acceptance dictionary need to be constructed)
            # if the current_searching_string is finished, then we compare the two
            pass

    return public_foreach(string,
                          next_state_fun,
                          init)


def run_dfa(doc: str, lst: list) -> dict:
    # accept when all accept states have their counter reduced to zero or less
    document = doc.split(" ")
    alphabet = parse_list(lst=lst)
    zero_states_list, zero_states = get_zero_states(lst=lst, alphabet=alphabet)
    states = build_states(lst=lst, zero_states=zero_states)
    # print(states)
    accept_states = get_accept_states(lst=lst, alphabet=alphabet)
    current_id = 0  # the word at current position, used to locate target for next state;
    current_searching_string = []  # a list contains all word id of current sentence
    for word_index in range(len(document)):
        current_word = document[word_index]
        previous_id = current_id
        active_states = states[previous_id][1:]  # active_states is what we are looking for for the current word.
        corresponding_init_word = current_word + "_init"  # 如果用miniwizpl,这里这种用word concatnate 的方法就不能用，需要直接找current_word + "_init" 的hash
        try:
            corresponding_id = alphabet[corresponding_init_word][0]
        except KeyError:
            corresponding_id = 0
        try:
            current_id = alphabet[current_word][0]  # !! I need to change it here so that I can use MINIWIZPL
        except KeyError:
            current_id = 0

        if current_id not in active_states:
            if corresponding_id in active_states:
                current_searching_string = [corresponding_id]
                # print("current_word=" + str(corresponding_init_word), "word_id=" + str(corresponding_id),
                #       "current_string=" + str(current_searching_string))
                current_id = corresponding_id  # update current_id, which is used as previous_id in the next iteration
            else:
                current_searching_string = []
                current_id = 0
                # print("current_word=" + str(current_word), "word_id=" + str(current_id),
                #       "current_string=" + str(current_searching_string))
        else:
            if current_id in zero_states and current_id in accept_states:
                # print("current_word=" + str(current_word), "word_id=" + str(current_id),
                #       "current_string=" + str([current_id]), "=> []")
                states[current_id][0] -= 1
                current_searching_string = []
            elif current_id in accept_states:
                current_searching_string.append(current_id)
                # print("current_word=" + str(current_word), "word_id=" + str(current_id),
                #       "current_string=" + str(current_searching_string), "=> []")
                for w in current_searching_string:
                    # print(w, states[w][0])
                    states[w][0] -= 1
                    # print(w, states[w][0])
                current_searching_string = []
            elif current_id in zero_states:  # maybe do not need this here
                current_searching_string = [current_id]
                # print("current_word=" + str(current_word), "word_id=" + str(current_id),
                #       "current_string=" + str(current_searching_string))
            else:
                current_searching_string.append(current_id)
                # print("current_word=" + str(current_word), "word_id=" + str(current_id),
                #       "current_string=" + str(current_searching_string))

    print(states)
    return states


def assert_whitelist(lst, file: str) -> bool:
    '''
    this function asserts that all items which are in the whitelist must contain in the text file
    '''
    # file_data = file_data.split()
    # file_string = SecretList([word_to_integer(c) for c in file_data])

    return True


# print(assert_whitelist(lst=whitelist, file=doc))

# print_emp(outputs, 'miniwizpl_test.cpp')
endTime = timeit.timeit()
print(endTime - startTime)

