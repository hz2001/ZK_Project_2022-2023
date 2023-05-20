# author: Herbert Zhang
# Date: 9/13/2022
# The very first draft of this project, currently not used, because could not integret with miniwizpl environment, and the algorithm is buggy with many edge cases.
import sys

whitelist = ["import numpy", "import socket", "import hello import world import", "something"]

# whitelist = ["hello world hello world numpy", "hello mini hello mini hello"]



# map each element into a state, returns alphabet
def parse_list(lst: list) -> dict:
    alphabet = {}
    counter = 1
    for words in lst:
        elements = words.split(" ")
        previous = None
        for word in elements:
            if word not in alphabet:
                alphabet[word] = [counter, 1, []]  # (state number, how many presented, what words follows it)
                counter += 1
            else:
                alphabet[word][1] += 1
            if previous is not None:
                if alphabet[word][0] not in alphabet[previous][2]:
                    alphabet[previous][2].append(alphabet[word][0])
            previous = word
    # the above code assumes that string "else" is not in our input document,
    # and we will replace all words which are not in our list to "else" keyword.
    alphabet["else"] = [0, 1, []]
    # return alphabet
    return update_alphabet(lst, alphabet, counter)


def update_alphabet(lst, alphabet, largest_id):

    print("alphabet before", alphabet)
    for words in lst:
        elements = words.split(" ")
        if len(elements) > 1:
            for word in elements[1:]:
                # this element appears as the zero state and regular state
                # we add another element to the alphabet to represent the first occurrence of that element
                if word == elements[0] and word + "_init" not in alphabet:
                    alphabet[word + "_init"] = [largest_id, 1, [alphabet[elements[1]][0]]]
                    alphabet[word][1] -= 1
                    # print(word, alphabet[word][2], alphabet[elements[1]][0])
                    try:
                        alphabet[word][2].remove(alphabet[elements[1]][0])
                    except ValueError:
                        print(word, alphabet[word][2], alphabet[elements[1]][0])
                        pass
                    break
                elif word == elements[0] and word + "_init" in alphabet:
                    alphabet[word + "_init"][1] += 1
                    alphabet[word][1] -= 1
                    if alphabet[elements[1]][0] not in alphabet[word + "_init"][2]:
                        alphabet[word + "_init"][2].append(alphabet[elements[1]][0])
                    break
        else:
            # len(elements) = 1, we ignore it
            pass

    print("alphabet after", alphabet)
    return alphabet

    # the length of elements is 1, treat the single word as the accept state


'''
alphabet = {'import': [1, 3, [2,3,6]], 'numpy': [2, 1, []], 'socket': [3, 1, []], 'hello': [4, 1, [5]], 'world': [5, 1, []], 'else': [0, 0, []]}       'import': [word id, occurrence, [follow ups]]
import numpy

Ex: states: {0:{counter,1,4}, 1:{counter,1,4,2,3,0}, 2:{counter,0,1,4}, 3:{counter,0,1,4},4:{counter,0,1,4,5},5{counter,0,1}}
'''


def get_zero_states(lst, alphabet):
    # loop through our list and assign each states
    zero_states = {}
    for words in lst:
        elements = words.split(" ")  # ["hello", "world"]
        if elements[0] + "_init" in alphabet:
            zero_states[alphabet[elements[0] + "_init"][0]] = True
        elif alphabet[elements[0]][
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


def build_states(lst: list, alphabet) -> dict:
    # lst represent black list or white list
    states = {}
    zero_states, zero_dic = get_zero_states(lst,
                                            alphabet)  # zero state are the collection of states when we encounter any word in the text file
    # initiate the states dictionary
    for word in alphabet:
        word_id = alphabet[word][0]
        # check if the word is accept or not; if yes, add 1 to the beginning, and when encounter it, reduce it to 0
        '''
        states[word_id] = occurrence_counter + next_states + zero_states
        '''
        states[word_id] = [alphabet[word][1]] + alphabet[word][2] + zero_states
    return states


# problem: if there exists a word that is by itself, such as "import", then it is accept state, however, in the string "import numpy", "import" is not accept state. which leads to some storage issue, i need to take track of that word seperatly
# we first assume that if a word is in accept state, then it cannot be in the unaccept state

def delete_redudent(state):
    # delete from element_states all corrsponding states which are finished
    # not going to work in the current state because the miniwizpl will not be able to do this

    return "success"


'''
alphabet = {'import': [1, 3, [2,3,6]], 'numpy': [2, 1, []], 'socket': [3, 1, []], 'hello': [4, 1, [5]], 'world': [5, 1, []], 'else': [0, 0, []]}       'import': [word id, occurrence, [follow ups]]
import numpy

Ex: states: {0:{counter,1,4}, 1:{counter,1,4,2,3,0}, 2:{counter,0,1,4}, 3:{counter,0,1,4},4:{counter,0,1,4,5},5{counter,0,1}}
'''


def run_dfa(doc: str, lst: list) -> dict:
    # accept when all accept states have their counter reduced to zero or less
    document = doc.split(" ")
    alphabet = parse_list(lst=lst)
    states = build_states(lst=lst, alphabet=alphabet)
    # print(states)
    zero_states_list, zero_states = get_zero_states(lst=lst, alphabet=alphabet)
    accept_states = get_accept_states(lst=lst, alphabet=alphabet)
    current_id = 0  # the word at current position, used to locate target for next state;
    current_searching_string = []  # a list contains all word id of current sentence
    for word_index in range(len(document)):
        current_word = document[word_index]
        previous_id = current_id
        active_states = states[previous_id][1:]  # active_states is what we are looking for for the current word.
        corresponding_init_word = current_word + "_init" # 如果用miniwizpl,这里这种用word concatnate 的方法就不能用，需要直接找current_word + "_init" 的hash
        try:
            corresponding_id = alphabet[corresponding_init_word][0]
        except KeyError:
            corresponding_id = 0
        try:
            current_id = alphabet[current_word][0] # !! I need to change it here so that I can use MINIWIZPL
        except KeyError:
            current_id = 0
        '''
        check if the current word is in our active states, 
            if so, we add current id to current_searching_string
            elif current word not in active states, it is not in init state nor following the current string
        then we need to check if the current word is in init state or accept state;
        '''
        if current_id not in active_states:
            if corresponding_id in active_states:
                current_searching_string = [corresponding_id]
                print("current_word=" + str(corresponding_init_word), "word_id=" + str(corresponding_id),
                      "current_string=" + str(current_searching_string))
                current_id = corresponding_id # update current_id, which is used as previous_id in the next iteration
            else:
                current_searching_string = []
                current_id = 0
                print("current_word=" + str(current_word), "word_id=" + str(current_id),
                      "current_string=" + str(current_searching_string))
        else:
            if current_id in zero_states and current_id in accept_states:
                print("current_word=" + str(current_word), "word_id=" + str(current_id),
                      "current_string=" + str([current_id]), "=> []")
                states[current_id][0] -= 1
                current_searching_string = []
            elif current_id in accept_states:
                current_searching_string.append(current_id)
                print("current_word=" + str(current_word), "word_id=" + str(current_id),
                      "current_string=" + str(current_searching_string), "=> []")
                for w in current_searching_string:
                    # print(w, states[w][0])
                    states[w][0] -= 1
                    # print(w, states[w][0])
                current_searching_string = []
            elif current_id in zero_states: # maybe do not need this here
                current_searching_string = [current_id]
                print("current_word=" + str(current_word), "word_id=" + str(current_id),
                      "current_string=" + str(current_searching_string))
            else:
                current_searching_string.append(current_id)
                print("current_word=" + str(current_word), "word_id=" + str(current_id),
                      "current_string=" + str(current_searching_string))

    print(states)
    return states


def assert_whitelist(lst, file: str) -> bool:
    '''
    this function asserts that all items which are in the whitelist must contain in the text file
    '''
    states = run_dfa(file, lst)
    for word_id in states:
        if states[word_id][0] > 0 and word_id != 0:
            # print(word_id, states[word_id][0])
            return False
    return True


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print("argument length not correct")
    elif type(args[0]) is not str:
        print("argument must have a file name string")
    else:
        with open(args[0], mode="r") as file:
            temp = [line for line in file.read().splitlines()]
            doc = " ".join(temp)
        file.close()
        alphabet = parse_list(whitelist)
        print("alphabet = " + str(alphabet))

        print("state dict = " + str(build_states(whitelist, alphabet)))

        print("zero_states = " + str(get_zero_states(whitelist, alphabet)))

        print("accept_states = " + str(get_accept_states(whitelist, alphabet)))

        print(doc)

        print(assert_whitelist(lst=whitelist, file=doc))


if __name__ == "__main__":
    main()
