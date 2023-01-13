# ZK_Project_2022-2023
This Repo handles the substring search problem in zero-knowledge to check if a document contains elements that we want based on Miniwizpl as the zero-knowledge environment. 

We provides two implementations, the first one uses a large DFA as the handler. Given a text file, the DFA would accept if the intended substrings presents properly in the file;

The second method uses counters to verify if a file contains the substrings we are looking for. Given a text file, this method would reduce the counter of a specific substring if a instance is found in the file, and it will certify in the end if all instances are found as intended. 


However, the second method is implemented with some limitations, as the substrings that is intended to be found/not found in the file must present as the following format: 
For each element in the list, if [A B C, A D C, E B F, E D C, ...] where A,E is must not 