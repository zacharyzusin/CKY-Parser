import sys
from collections import defaultdict
from math import fsum
from math import isclose

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        
        non_terminals = set(self.lhs_to_rules.keys())
        rhs_symbols = set()
        for rules in self.rhs_to_rules.values():
            for lhs, rhs, _ in rules:
                rhs_symbols.update(rhs)
        terminals = rhs_symbols - non_terminals

        for lhs, rules in self.lhs_to_rules.items():
            prob_sum = fsum(rule[2] for rule in rules)
            if not isclose(prob_sum, 1.0, rel_tol=1e-9):
                return False

            for rule in rules:
                rhs = rule[1]
                if len(rhs) == 2 and not (rhs[0] in non_terminals and rhs[1] in non_terminals):
                    return False
                elif len(rhs) == 1 and not (rhs[0] in terminals or rhs[0] in non_terminals):
                    return False
                elif len(rhs) > 2:
                    return False

        return True

if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)
        if grammar.verify_grammar():
            print("The grammar is a valid PCFG in CNF.")
        else:
            print("The grammar is not a valid PCFG in CNF.")