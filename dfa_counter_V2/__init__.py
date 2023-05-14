import sys
from .counter_substring_search import *
from miniwizpl import *
from miniwizpl.expr import *

sys.path.append("/usr/src/app/examples/substring_search/common")
import util

def main(target_dir, prime, prime_name, size, operation):
    # Importing ENV Var & Checking if prime meets our requirement

    assert len(sys.argv) == 6, "Invalid arguments"
    _, target_dir, prime, prime_name, size, operation = sys.argv
    file_name = "stringlist_search"
    set_field(int(prime))

    try:
        assert util.check_prime() == True
    except:
        print("no equivalent prime (2305843009213693951) in ccc.txt")
        sys.exit(1)

    # Prepping target text and substrings

    if operation == "test":
        corpus = util.generate_text(int(size))
        stringList = util.generate_target(
            corpus, file_name, length=2, n_string=4)
        target_counterList = [1 for i in stringList]
        print("Test (First 10 Strings): ", corpus[0:10])
        print("Actual text length:", len(corpus))

    else:
        stringList = ["one two", "three five"]

        with open("/usr/src/app/examples/dfa_test_input.txt", "r") as f:
            corpus = f.read()
        corpus = corpus.split()
        print("Text: ", corpus, "\n")

    print("Target: ", stringList, "\n")

    # Transform the text file to search into miniwizpl format

    file_string = SecretList([util.word_to_integer(_str) for _str in corpus])

    zero_state = tuple([0] * len(stringList))
    zero_state = stateCal(zero_state)

    # Build and traverse a DFA
    stateLength = len(stringList)
    dfa = dfa_from_string(stringList)

    print("Traversing DFA")

    counterList = run_dfa(dfa=dfa, document=file_string, zeroState=zero_state)
    print("Output Assertion")

    print("Running Poseidon Hash")
    util.run_poseidon_hash(file_string)
    # assert if the counterList we output matches the counterList provided

    for i in range(stateLength):
        assert0(
            counterList[i] - target_counterList[i]
        )  # TODO: currently set to be asserting each string to appear once

    global assertions  # TODO: ask is it safe to do so here?

    # claim a return_state so that we don't have to change the test file.
    if False in assertions:
        print("DFA did not reached the accept state \n")
    else:
        print("DFA successfully reached the accept state \n")

    print("Generating Output \n")
    print_ir0(target_dir + "/" + f"{file_name}_{prime_name}_{size}")


if __name__ == "__main__":
    main(*sys.argv[1:])
