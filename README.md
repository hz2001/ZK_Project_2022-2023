# Substring Search -- Zeroknowledge Project 2022-2023
This repository contains a example to the substring search problem in zero-knowledge under Miniwizpl.

### Introduction

First to understand about [zero-knowledge](https://en.wikipedia.org/wiki/Zero-knowledge_proof#:~:text=Zero%2Dknowledge%3A%20if%20the%20statement,the%20prover%20knows%20the%20secret.): In a typical zk proof, there are tro parties, the verifier party and the prover party, and the prover want to prove certain facts to the varifier without reveal the evidences that he has. A zk-proof can be applied to hide evidences from the prover. In this project, we are aiming to solve the substring search problem. To be more specific, the substring search method we built is able to find if there are certain words contained in a document given a hidden document. 

The code are mainly standing alone with no dependencies (especially the DFA builders). Yet, they do depend on miniwizpl as the environment, make sure this package is installed by using   
`python3 -m pip install miniwizpl hashlib`

Then clone the repository, run:  

`git clone https://github.com/hz2001/ZK_Project_2022-2023.git`

## Attempted Implementations

We provides two attempted implementations of this problem in this repository.

All implementations have 
> The only fully finished method is the dfa_counter_V2 module. An additional version of the same code is copied into the `SIEVE` branch of this repo for merging into the SIEVE repository containing other ZK proofs.

### [I. The Big DFA](./dfa_original_V1/)
The dfa_original_V1 folder contains the progress that we made for code implemented with triditional DFA. 

In this method, we use a big DFA that contains every possible steps of the workflow given the substrings. 

The DFA looks like the following given `stringlist = ["import numpy", "avoid child abuse"]`: 

```
DFA = {((0, 0), avoid): (0, 1),
 ((0, 0), import): (1, 0),
 ((0, 1), child): (0, 2),
 ((0, 1), abuse): (0, 0),
 ((0, 1), avoid): (0, 0),
 ((0, 1), import): (1, 0),
 ((0, 1), numpy): (0, 0),
 ((1, 0), child): (0, 0),
 ((1, 0), abuse): (0, 0),
 ((1, 0), avoid): (0, 1),
 ((1, 0), import): (0, 0),
 ((1, 0), numpy): ((255, 255), 0),
 ((0, 2), child): (0, 0),
 ((0, 2), abuse): (0, (255, 255)),
 ((0, 2), avoid): (0, 0),
 ((0, 2), import): (1, 0),
 ((0, 2), numpy): (0, 0),
 (((255, 255), 0), avoid): ((255, 255), 1),
 ((0, (255, 255)), import): (1, (255, 255)),
 (((255, 255), 1), child): ((255, 255), 2),
 (((255, 255), 1), abuse): ((255, 255), 0),
 (((255, 255), 1), avoid): ((255, 255), 0),
 (((255, 255), 1), import): ((255, 255), 0),
 (((255, 255), 1), numpy): ((255, 255), 0),
 ((1, (255, 255)), child): (0, (255, 255)),
 ((1, (255, 255)), abuse): (0, (255, 255)),
 ((1, (255, 255)), avoid): (0, (255, 255)),
 ((1, (255, 255)), import): (0, (255, 255)),
 ((1, (255, 255)), numpy): ((255, 255), (255, 255)),
 (((255, 255), 2), child): ((255, 255), 0),
 (((255, 255), 2), abuse): ((255, 255), (255, 255)),
 (((255, 255), 2), avoid): ((255, 255), 0),
 (((255, 255), 2), import): ((255, 255), 0),
 (((255, 255), 2), numpy): ((255, 255), 0)}
```
equvilently, it looks like this for miniwizpl to process:

```
DFA = {((0, 0), 423132159): (0, 1),
 ((0, 0), 1822522148): (1, 0),
 ((0, 1), 1860498228): (0, 2),
 ((0, 1), 1392842200): (0, 0),
 ((0, 1), 423132159): (0, 0),
 ((0, 1), 1822522148): (1, 0),
 ((0, 1), 971933143): (0, 0),
 ((1, 0), 1860498228): (0, 0),
 ((1, 0), 1392842200): (0, 0),
 ((1, 0), 423132159): (0, 1),
 ((1, 0), 1822522148): (0, 0),
 ((1, 0), 971933143): ((255, 255), 0),
 ((0, 2), 1860498228): (0, 0),
 ((0, 2), 1392842200): (0, (255, 255)),
 ((0, 2), 423132159): (0, 0),
 ((0, 2), 1822522148): (1, 0),
 ((0, 2), 971933143): (0, 0),
 (((255, 255), 0), 423132159): ((255, 255), 1),
 ((0, (255, 255)), 1822522148): (1, (255, 255)),
 (((255, 255), 1), 1860498228): ((255, 255), 2),
 (((255, 255), 1), 1392842200): ((255, 255), 0),
 (((255, 255), 1), 423132159): ((255, 255), 0),
 (((255, 255), 1), 1822522148): ((255, 255), 0),
 (((255, 255), 1), 971933143): ((255, 255), 0),
 ((1, (255, 255)), 1860498228): (0, (255, 255)),
 ((1, (255, 255)), 1392842200): (0, (255, 255)),
 ((1, (255, 255)), 423132159): (0, (255, 255)),
 ((1, (255, 255)), 1822522148): (0, (255, 255)),
 ((1, (255, 255)), 971933143): ((255, 255), (255, 255)),
 (((255, 255), 2), 1860498228): ((255, 255), 0),
 (((255, 255), 2), 1392842200): ((255, 255), (255, 255)),
 (((255, 255), 2), 423132159): ((255, 255), 0),
 (((255, 255), 2), 1822522148): ((255, 255), 0),
 (((255, 255), 2), 971933143): ((255, 255), 0)}
```

After building the DFA, we will have to iterate through the secret document using the `run_dfa()` function.

#### Example Useage
The string_search.py file is runable on its own. 

To run this file, run:  
```
cd dfa_original_V1
python3 stringlist_search.py
```

The sls_debug.py is intended to be run inside the docker container. If settled with the container, run:
```
python3 sls_debug.py your_target_directory your_prime_number your_prime_name your_document_size operation
```

#### Running Mannuly

Inside a .py file or .ipynb file, do 
```
from sls_debug.py import *
```

Define your secret document: 

```
file_string = SecretList([word_to_integer(_str) for _str in <your file>])
```


Initiate variables needed, do
```
string_target = <Your Target List>

accept_state = 255
accept = tuple([255] * len(string_target))
accept = stateCal(accept)
zero_state = tuple([0] * len(string_target))
zero_state = stateCal(zero_state)
```

Build the DFA, do
```
# Build and traverse a DFA
dfa = dfa_from_string(string_target, accept_state)
```

Run DFA, do
```
stateLength = len(string_target)
latest_state = run_dfa(dfa, file_string, zero_state, accept, stateLength)
```

Asserting Results, do
```
assert0(latest_state - accept)
``` 



#### limitations
Originally, we thought [THIS METHOD](./dfa_original_V1.0/stringlist_search.py) would work fine in all cases to find strings within the stringList that appears at least once in the document; however, there are some cases that this method would not work properly. So we have started a debuging process for this method, which we stated in the [Debugging File](./dfa_original_V1.0/sls_debug.py). In this file, we have proposed a solution for the existing bug, but our solution wouldn't work with the current version of miniwizpl, since it does not support bitwise operators yet. If Miniwizpl has been updated in the future, we can look into this method to update it as needed.

### [II. The DFA with Counter](./)

This method uses counters to verify if a file contains the substrings we are looking for. Given a list of substrings, this method will take track of a counter of each substrings, then increment counters when they are find in the document to be verified. It will certify in the end if all instances are found as intended. 

#### limitations
However, the second method is implemented with some limitations, as the substrings that is intended to be found/not found in the file must not present with the following format:
1. the starting string must present in the starting position for all substrings, so does the last string. For example, ["hello world peace", "hello hi"] is valid, but ["hello world peace", "hi hello"] is not ok, and ["worry hello world", "hello hi"] is not ok as well.

2. one substring cannot be a substring of another one. For example, ["hello world peace", "hello world"] is not ok. 

**Since this method have so much problem without easy solutions, we rewrote this method in dfa_counter_V2, which is shown below.**

#### dfa_counter_V2
In the dfa_counter_V2 module, we introduced a fully functional solution of the substring search problem using counters. It also supports verifications of multiple occurance of the same word in the hidden document. 


Similarly to the structure of the original version, the DFA looks like the following given `stringlist = ["import numpy", "avoid child abuse"]`: 

```
DFA = {((0, 0), 'avoid'): (0, 1),
  ((0, 0), 'import'): (1, 0),
  ((0, 1), 'avoid'): (0, 1),
  ((0, 1), 'child'): (0, 2),
  ((0, 1), 'import'): (1, 0),
  ((1, 0), 'avoid'): (0, 1),
  ((1, 0), 'import'): (1, 0),
  ((1, 0), 'numpy'): (0, 0),
  ((0, 2), 'abuse'): (0, 0),
  ((0, 2), 'avoid'): (0, 1),
  ((0, 2), 'import'): (1, 0)}
```
equvilently, it looks like this for miniwizpl to process:

```
DFA = {((0, 0), 1822522148): [0, 0],
 ((0, 0), 423132159): [0, 0],
 ((1, 0), 1822522148): [0, 0],
 ((1, 0), 423132159): [0, 0],
 ((1, 0), 971933143): [1, 0],
 ((0, 1), 1860498228): [0, 0],
 ((0, 1), 1822522148): [0,'; 0],
 ((0, 1), 423132159): [0, 0],
 ((0, 2), 1822522148): [0, 0],
 ((0, 2), 423132159): [0, 0],
 ((0, 2), 1392842200): [0, 1]}
```


#### Example Useage
The string_search.py file is runable on its own. 

To run this file, run:  
```
cd dfa_counter_V2
```

The coutner_stringlist_search.py is intended to be run inside the docker container. If settled with the container, run:
```
python3 countner_stringlist_search.py your_target_directory your_prime_number your_prime_name your_document_size operation
```

#### Running Mannuly

Inside a .py file or .ipynb file, do 
```
from countner_stringlist_search.py import *
```

Define your secret document: 

```
file_string = SecretList([word_to_integer(_str) for _str in <your file>])
```


Initiate variables needed, do
```
zero_state = tuple([0] * len(string_target))
zero_state = statement.stateCal(zero_state)

counterListTarget = <specify the number of instance you want for each substring>
```

To build DFA, do
```
dfa,counterDict = statement.dfa_from_string(string_target)
```

Run DFA, do
```
counterList = statement.run_dfa(
    dfa=dfa, 
    document=file_string, 
    zeroState=zero_state, 
    counterDict=counterDict, 
    lstLen=len(string_target))
```

Asserting Results, do
```
for i in range(len(counterListTarget)):
    self.assertGreaterEqual(val_of(counterList[i]), counterListTarget[i])
``` 



