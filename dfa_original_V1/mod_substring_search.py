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
        hash += (ord(word[i]) << 8*i)

    return hash

# a Python function to create a dfa from a string
# we assume a default transition back to 0
def dfa_from_string(string):
    next_state = {}
    text = string.split()
    alphabet = set(text)

    for i in range(len(text)):
        for j in alphabet:
            if j == text[i]:
                if i == len(text) - 1:
                    # accept state
                    next_state[(i, word_to_integer(j))] = accept_state
                else:
                    next_state[(i, word_to_integer(j))] = i+1
            else:
                for k in range(len(text)):
                    try:
                        conc = " ".join(text[k:i])
                        if (string.index(conc +" " + j) == 0 or string.index(j)==0) and k <= i:
                            

                                next_state[(i, word_to_integer(j))] = i - k + 1
                                break
                    except ValueError:
                        pass
    return next_state

strings_present = [
    'os.system(f"python client_request.py {param_string}")',
    'import '
    ]

strings_not_present = [
    'import socket'
    ]

# read the target file & convert to secret string
with open(sys.argv[1], 'r') as f:
    file_data = f.read()

file_data = file_data.split()
file_string = SecretList([word_to_integer(c) for c in file_data])

# def public_foreach(ls, fn, init):
# accumulator = init
# for x in ls:
#    accumulator = fn(x, accumulator)
# return accumulator

# run a dfa
def run_dfa(dfa, string):
    def next_state_fun(word, state):
        output = 0

        for (dfa_state, dfa_word), next_state in dfa.items():
            output = mux((state == dfa_state) & (word == dfa_word),
                         next_state,
                         output)

        output = mux(state == accept_state, accept_state, output)
        return output

    return public_foreach(string,
                          next_state_fun,
                          0)

# define the ZK statement
outputs = []
for s in strings_present:
    dfa = dfa_from_string(s)
    outputs.append(run_dfa(dfa, file_string) == accept_state)
for s in strings_not_present:
    dfa = dfa_from_string(s)
    outputs.append(run_dfa(dfa, file_string) != accept_state)

print(outputs)
# compile the ZK statement to an EMP file
output = functools.reduce(lambda a, b: a & b, outputs)
print_emp(output, 'miniwizpl_test.cpp')
