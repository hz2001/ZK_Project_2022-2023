import sys

whitelist = ["hello world hello world numpy"]



'''1:import; 2:numpy; 3:socket; 4:hello; 5:world'''
# map each element into a state
def parse_list(lst: list) -> dict:
    alphabet = {}
    counter = 1
    for words in lst:
        elements = words.split(" ")
        previous = None
        for i in elements:
            if i not in alphabet:
                alphabet[i] = [counter, 1, []]  # (state number, how many presented )
                counter += 1
            else:
                alphabet[i][1] += 1
            if previous is not None:
                alphabet[previous][2].append(alphabet[i][0])
            previous = i
    # the above code assumes that string "else" is not in our input document,
    # and we will replace all words which are not in our list to "else" keyword.
    alphabet["else"] = [0, 1, []]
    return alphabet


def get_zero_states(lst, alphabet):
    # loop through our list and assign each states
    zero_states = {}
    for words in lst:
        elements = words.split(" ") # ["hello", "world"]
        if alphabet[elements[0]][0] not in zero_states: # elements[0] is the first item, alphabet[elements[0]][0] is word id
            zero_states[alphabet[elements[0]][0]] = True
    return [state for state in zero_states], zero_states # returns a list and a dic which have the same elements


def get_accept_states(lst, alphabet):
    result = {}
    for words in lst:
        elements = words.split(" ")
        if len(elements) != 1: # if len(element) == 1 then it is a special case where it might be the first
            result[alphabet[elements[-1]][0]] = True
        else:
            result[alphabet[elements[-1]][0]] = True # *maybe need to change* currently we don't care about the instance when there is a word both at accept state and in the unaccept state
    return result


def build_states(lst:list) -> dict:
    # lst represent black list or white list
    alphabet = parse_list(lst)
    states = {}
    zero_states, zero_dic = get_zero_states(lst, alphabet) # zero state are the collection of states when we encounter any word in the text file
    # initiate the states dictionary
    for word in alphabet:
        word_id = alphabet[word][0]
        # check if the word is accept or not; if yes, add 1 to the beginning, and when encounter it, reduce it to 0
        '''
        states[word_id] = occurrence_counter + next_states + zero_states
        '''
        states[word_id] =  [alphabet[word][1]] + alphabet[word][2] + zero_states
    return states


def run_dfa(doc: str, lst: list) -> dict:
    # accept when all accept states have their counter reduced to zero or less
    document = doc.split(" ")
    states = build_states(lst=lst)
    # print(document)
    print(states)
    alphabet = parse_list(lst=lst)
    zero_states_list, zero_states = get_zero_states(lst=lst, alphabet=alphabet)
    accept_states = get_accept_states(lst=lst, alphabet=alphabet)
    current_id = 0  # the word at current position, used to locate target for next state;
    current_searching_string = []  # a list contains all word id of current sentence
    for word_index in range(len(document)):
        current_word = document[word_index]
        previous_id = current_id
        active_states = states[previous_id][1:]  # active_states is what we are looking for for the current word.
        try:
            current_id = alphabet[current_word][0]
        except KeyError:
            current_id = 0
        '''
        check if the current word is in our active states, 
            if so, we add current id to current_searching_string
            elif current word not in active states, it is not in init state nor following the current string
        then we need to check if the current word is in init state or accept state;
        '''
        if current_id not in active_states:
            print("current_word=" + str(current_word), "word_id=" + str(current_id),
                  "current_string=" + str(current_searching_string) + "=> []")
            current_searching_string = []
            current_id = 0

        else:
            if current_id in zero_states:
                current_searching_string = [current_id]
                print("current_word=" + str(current_word), "word_id=" + str(current_id),
                      "current_string=" + str(current_searching_string))
            elif current_id in accept_states:
                current_searching_string.append(current_id)
                print("current_word=" + str(current_word), "word_id=" + str(current_id),
                      "current_string=" + str(current_searching_string), "=> []")
                for w in current_searching_string:
                    # print(w, states[w][0])
                    states[w][0] -= 1
                    # print(w, states[w][0])
                current_searching_string = []
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

        print("alphabet = " + str(parse_list(whitelist)))

        print("state dict = " + str(build_states(whitelist)))

        print("zero_states = " + str(get_zero_states(whitelist, parse_list(whitelist))))

        print("accept_states = " + str(get_accept_states(whitelist, parse_list(whitelist))))

        print(doc)

        print(assert_whitelist(lst=whitelist, file=doc))


if __name__ == "__main__":
    main()



