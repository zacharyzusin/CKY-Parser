import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar):
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        n = len(tokens)
        table = [[set() for i in range(n+1)] for j in range(n+1)]

        for i, word in enumerate(tokens):
            for rule in self.grammar.rhs_to_rules.get((word,), []):
                table[i][i+1].add(rule[0])

        for length in range(2,n+1):
            for i in range(n-length+1):
                j = i + length
                for k in range(i+1,j):
                    for lhs, rules in self.grammar.lhs_to_rules.items():
                        for rule in rules:
                            B = rule[1][0][0]
                            C = rule[1][0][1]
                            if B in table[i][k] and C in table[k][j]:
                                table[i][j].add(lhs)
                                

        return self.grammar.startsymbol in table[0][n]
       
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        n = len(tokens)
        table = {}
        probs = {}

        for i, word in enumerate(tokens):
            table[(i, i+1)] = {}
            probs[(i, i+1)] = {}
            for rule in self.grammar.rhs_to_rules[(word,)]:
               if (word,) in self.grammar.rhs_to_rules:
                for rule in self.grammar.rhs_to_rules[(word,)]:
                    nonterminal = rule[0]
                    prob = rule[2]
                    table[(i, i+1)][nonterminal] = word
                    probs[(i, i+1)][nonterminal] = math.log(prob)        

        for length in range(2, n+1):
            for i in range(n-length+1):
                j = i+length
                table[(i, j)] = {}
                probs[(i, j)] = {}
                for k in range(i+1, j):
                    for B, rules_B in table[(i, k)].items():
                        for C, rules_C in table[(k, j)].items():
                            if (B, C) in self.grammar.rhs_to_rules:
                                for rule in self.grammar.rhs_to_rules[(B, C)]:
                                    A, _, rule_prob = rule
                                    prob = math.log(rule_prob) + probs[(i, k)][B] + probs[(k, j)][C]
                                    if A not in probs[(i, j)] or prob > probs[(i, j)][A]:
                                        table[(i, j)][A] = ((B, i, k), (C, k, j))
                                        probs[(i, j)][A] = prob

        return table, probs

def get_tree(chart,i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    if i + 1 == j:
        return (nt, chart[(i, j)][nt])
    
    left_bp, right_bp = chart[(i, j)][nt]
    left_nt, left_i, left_j = left_bp
    right_nt, right_i, right_j = right_bp
    
    left_tree = get_tree(chart, left_i, left_j, left_nt)
    right_tree = get_tree(chart, right_i, right_j, right_nt)
    
    return (nt, left_tree, right_tree)
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file)
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        table, probs = parser.parse_with_backpointers(toks)
        tree = get_tree(table, 0, len(toks), grammar.startsymbol)
        print(tree)
        
