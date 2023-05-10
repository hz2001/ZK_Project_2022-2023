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


def dfa_from_string(target_list, accept_state):

    '''
      - target_list: A list of sub texts to look for

      - state/init_state/prev_state/curr_state: Pointer representing an index of one of sub texts to look at
      
      - states: A list of states
      
      - states_pos: pointer of states list
      
      - DFA: Resulting DFA
    
    '''

    init_state = [0] * len(target_list) # init_state = [0, 0, 0, 0]
    DFA = {} # DFA to return
    target_set = set(' '.join(target_list).split()) # target_set = {'socket', 'import', 'sys', 'hello', 'numpy', 'world'}

    states = [init_state]  # keep track of all states # initially states = [[0, 0, 0, 0]] for four sets of sub texts
    piv_pos = 0
    finished = False  # not all accepted

    '''
        1) The parent loop keeps iteration till the states list stops growing 
           This is when the DFA is built and state [255, ..., 255] is reached
          
          a) For every iteration of the parent loop, pivot state is picked, from which the subsequent new states get derived
          b) Whether or not the states list is growing is determined by b) n_states, which is initiated at the beginning and compared with len(states) at the end of the loop (Step 5)

        2) The outer loop goes over all words in target_set

        3) The inner loop goes over all sub texts in target_list

        4) IF statements in the inner loop:
          a) Checks whether or not the string at the current index of sub text matches the word in the target_set 
          b) Checks whether or not visiting the last element of the sub text
              - if true, accept (no more work for this sub text)
              - else, move the index to next substring of the sub text

        5) If a new state is created (not equal to the pivot_state), it will be added to states list and 

        6) If there was no increment to states, i.e., DFA is built , it ends the outermost loop

        To reiterate, the parent loop keeps iterating till all the sub texts reach accept states. Correspondingly, piv_pos keeps getting incremented till then
        
    '''
    # 1) Parent loop
    while not finished:
        pivot_state = states[piv_pos] # a) Picking a pivot state to derive from
        n_states = len(states) # b) This value is compared at 6) if the states list grew in this iteration or not (If not, the DFA is built and the function ends)

        # 2) outer loop over all words in the target set = {'socket', 'import', 'sys', 'hello', 'numpy', 'world'}
        for word in target_set:  
            curr_state = pivot_state.copy() # By copying pivot_state, the next curr_state can derive from the latest
            
            # 3) inner loop over the list of sub texts
            for tgt_idx in range(len(target_list)):
                if pivot_state[tgt_idx] != accept_state:

                    '''
                      4) Series of IF statements
                      
                        4-a) If the current index of the subtext it's looking at is same word as the word in the target set

                             ==>> 4-b) If currently visiting the last string of the current sub text

                                         ==>> the current state of the current sub text will move into accept_state
                                 
                                      Else (If not currently visiting the end string)

                                         ==>> the state/pointer of the current sub text will be incremented
                        
                             Else (If different word from the current):
                        
                                ==>> The curr_state corresponding to the sub text will be set 0
                                     Meaning, if the previous state of this index was already 1, but the current word does not match, the sub text should be considered unmatch
                    '''

                    if word == target_list[tgt_idx].split()[pivot_state[tgt_idx]]: # 4-a) Check word match
                        if islast(pivot_state[tgt_idx], target_list[tgt_idx]): # 4-b) Check if visiting last words of a sub text (e.g., 'socket' of 'import socket')
                            curr_state[tgt_idx] = accept_state
                        else:
                            curr_state[tgt_idx] += 1
                    else: 
                        curr_state[tgt_idx] = 0

            # 5) Check if a new state is created
            if not equals(curr_state, pivot_state):
                states.append(curr_state)
                DFA[tuple(pivot_state), word_to_integer(word)] = tuple(curr_state)
                
        # 6) Check if an appropriate DFA is built
        if n_states == len(states):
            finished = True
        else:
            piv_pos += 1
    return DFA



def run_dfa(dfa, string, zero_state, accept):
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

        curr_state = mux(initial_state == accept, accept, curr_state)  # TODO: this line might need to be changed for the counter.

        return curr_state
    latest_state=reduce(next_state_fun,string, zero_state)
    return latest_state

def main(target_dir, prime, prime_name, size, operation):

    # Importing ENV Var & Checking if prime meets our requirement

    assert len(sys.argv) == 6, "Invalid arguments"
    _, target_dir, prime, prime_name, size, operation = sys.argv
    file_name="stringlist_search"
    set_field(int(prime))

    try:
        assert check_prime()== True
    except:
        print("no equivalent prime (2305843009213693951) in ccc.txt")
        sys.exit(1)


    # Prepping target text and substrings

    if operation =="test":
        corpus=generate_text(int(size))
        substring_len=2**int(size)
        piv_len=2**int(size)
        string_target=generate_target(corpus, file_name, substring_len=substring_len, piv_len=piv_len)
        print("Test (First 10 Strings): ",corpus[0:10])
        print("Actual text length:", len(corpus))

    else:
        string_target = ['one two', 'three four']

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
    print("\n", "Latest State: ",val_of(latest_state), "\n")

    # TODO: instead of comparing the run_dfa result, we will need to compare the actual_counter with the expected_counter.

    print('accept ', accept)
    print('accept_state ', accept_state)

    if val_of(latest_state)==accept:
        print("DFA successfully reached the accept state \n")
    else:
        print("DFA did not reached the accept state \n")

    print("Generating Output for",file_name, "\n")
    print_ir0(target_dir + "/" + f"{file_name}_{prime_name}_{size}")

if __name__ == '__main__':
    main(*sys.argv[1:])