# This file is a copy of the test for stringlist_search.py except that it is used to test the method of dfa_counter.
import sys
import unittest
from unittest.mock import patch
from miniwizpl import *
from miniwizpl.expr import *

sys.path.append("/usr/src/app/examples/substring_search/IR0/ZK_Project_2022-2023")
import dfa_counter_V2 as statement

sys.path.append("/usr/src/app/examples/substring_search/common")
import util

class TestStatement(unittest.TestCase):
    
    def test_base(self):

        '''
            A base case to pass, target strings being at the beginning of the corpus 
            No trickiness involved
        '''

        string_target = ['one two', 'three four']
        corpus = 'one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen'
        corpus = corpus.split()
        file_string = SecretList([util.word_to_integer(_str) for _str in corpus])

        accept_state = 255
        accept = tuple([255] * len(string_target))
        accept = statement.stateCal(accept)
        zero_state = tuple([0] * len(string_target))
        zero_state = statement.stateCal(zero_state)

        dfa = statement.dfa_from_string(string_target, accept_state)
        latest_state = statement.run_dfa(dfa, file_string, zero_state, accept)
        self.assertEqual(val_of(latest_state), accept)
        self.assertNotEqual(val_of(latest_state), zero_state)

    def test_intermediate(self):

        '''
            An intermediate case to pass, target strings in the middle of the corpus 
            The second element of the first target and the first element of the second target overlaps
        '''

        string_target = ['three four', 'four five']
        corpus = 'one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen'
        corpus = corpus.split()
        file_string = SecretList([util.word_to_integer(_str) for _str in corpus])

        accept_state = 255
        accept = tuple([255] * len(string_target))
        accept = statement.stateCal(accept)
        zero_state = tuple([0] * len(string_target))
        zero_state = statement.stateCal(zero_state)

        dfa = statement.dfa_from_string(string_target, accept_state)
        latest_state = statement.run_dfa(dfa, file_string, zero_state, accept)
        self.assertEqual(val_of(latest_state), accept)
        self.assertNotEqual(val_of(latest_state), zero_state)


    def test_intermediate2(self):

        '''
            An intermediate case to pass, one of the target strings at the beginning and the other at the end of the corpus 
        '''

        string_target = ['one two', 'fourteen fifteen']
        corpus = 'one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen'
        corpus = corpus.split()
        file_string = SecretList([util.word_to_integer(_str) for _str in corpus])

        accept_state = 255
        accept = tuple([255] * len(string_target))
        accept = statement.stateCal(accept)
        zero_state = tuple([0] * len(string_target))
        zero_state = statement.stateCal(zero_state)

        dfa = statement.dfa_from_string(string_target, accept_state)
        latest_state = statement.run_dfa(dfa, file_string, zero_state, accept)
        self.assertEqual(val_of(latest_state), accept)
        self.assertNotEqual(val_of(latest_state), zero_state)


    def test_advance(self):

        '''
            An advance case to pass, three targets
            One of the target strings in the middle of the corpus, another overlapping, and the other at the end of the corpus 
        '''

        string_target = ['one two', 'two three', 'fourteen fifteen']
        corpus = 'one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen'
        corpus = corpus.split()
        file_string = SecretList([util.word_to_integer(_str) for _str in corpus])

        accept_state = 255
        accept = tuple([255] * len(string_target))
        accept = statement.stateCal(accept)
        zero_state = tuple([0] * len(string_target))
        zero_state = statement.stateCal(zero_state)

        dfa = statement.dfa_from_string(string_target, accept_state)
        latest_state = statement.run_dfa(dfa, file_string, zero_state, accept)
        self.assertEqual(val_of(latest_state), accept)
        self.assertNotEqual(val_of(latest_state), zero_state)


    def test_fail(self):

        '''
            A base case to fail, target strings being at the beginning of the corpus 
            'five' comes immediately after 'three' in string_target, skipping 'four'
        '''

        string_target = ['one two', 'three five']
        corpus = 'one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen'
        corpus = corpus.split()
        file_string = SecretList([util.word_to_integer(_str) for _str in corpus])

        accept_state = 255
        accept = tuple([255] * len(string_target))
        accept = statement.stateCal(accept)
        zero_state = tuple([0] * len(string_target))
        zero_state = statement.stateCal(zero_state)

        dfa = statement.dfa_from_string(string_target, accept_state)
        latest_state = statement.run_dfa(dfa, file_string, zero_state, accept)
        self.assertEqual(val_of(latest_state), zero_state)
        self.assertNotEqual(val_of(latest_state), accept)


if __name__ == '__main__':
    unittest.main()

