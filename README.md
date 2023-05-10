# ZK_Project_2022-2023
This Repo handles the substring search problem in zero-knowledge to check if a document contains elements that we want based on Miniwizpl as the zero-knowledge environment. 

We provides two implementations, the first one uses a large DFA as the handler. Given a text file, the DFA would accept if the intended substrings presents properly in the file;

The second method uses counters to verify if a file contains the substrings we are looking for. Given a text file, this method would reduce the counter of a specific substring if a instance is found in the file, and it will certify in the end if all instances are found as intended. 


However, the second method is implemented with some limitations, as the substrings that is intended to be found/not found in the file must present as the following format: 
For each element in the list, if [A B C, A D C, E B F, E D C, ...] where A,E is must not 

### dfa_original_V1.0
The container dfa_original_V1.0 folder contains the progress that we made for code implemented with triditional DFA. Originally, we thought [THIS METHOD](./dfa_original_V1.0/stringlist_search.py) would work fine in all cases to find strings within the stringList that appears at least once in the document; however, there are some cases that this method would not work properly. So we have started a debuging process for this method, which we stated in the [Debugging File](./dfa_original_V1.0/sls_debug.py). In this file, we have proposed a solution for the existing bug, but our solution wouldn't work with the currently version of miniwizpl, since it does not support bitwise operators yet. If Miniwizpl has been updated in the future, we can look into this method to update it as needed.

