# CKY Parser Implementation

This project implements the Cocke-Kasami-Younger (CKY) algorithm for parsing Context-Free Grammars (CFG) and Probabilistic Context-Free Grammars (PCFG). The implementation includes functionality for membership checking, parsing with backpointers, and parse tree retrieval.

## Project Overview

The parser is designed to work with grammars in Chomsky Normal Form and was tested on the ATIS (Air Travel Information Services) subset of the Penn Treebank. This implementation can:
- Verify if a grammar is a valid PCFG in Chomsky Normal Form
- Check if a sentence is in the language defined by the grammar
- Generate the most probable parse for a given sentence
- Reconstruct parse trees from the parsing chart

## Files in the Repository

- `cky.py`: Contains the main CKY parser implementation
- `grammar.py`: Implements the PCFG grammar class for reading and verifying grammars
- `evaluate_parser.py`: Script for evaluating parser performance against a test set

## Usage

### 1. Grammar Verification
To verify if a grammar is valid:
```python
from grammar import Pcfg

with open('atis3.pcfg', 'r') as grammar_file:
    grammar = Pcfg(grammar_file)
```

### 2. Basic Parsing
To check if a sentence is in the language:
```python
from cky import CkyParser

parser = CkyParser(grammar)
tokens = ['flights', 'from', 'miami', 'to', 'cleveland', '.']
is_valid = parser.is_in_language(tokens)
```

### 3. Full Parsing with Tree Generation
To get the most probable parse tree:
```python
table, probs = parser.parse_with_backpointers(tokens)
tree = parser.get_tree(table, 0, len(tokens), grammar.startsymbol)
```

### 4. Evaluating Parser Performance
To evaluate the parser against a test set:
```bash
python evaluate_parser.py atis3.pcfg atis3_test.ptb
```

## Implementation Details

### Grammar Format
The grammar should be in Chomsky Normal Form (CNF) with rules in one of these formats:
- A → BC (where A, B, C are nonterminals)
- A → a (where A is a nonterminal and a is a terminal)

### Parser Features
1. **Grammar Verification**:
   - Checks for valid CNF format
   - Verifies probability distributions sum to 1 for each nonterminal

2. **CKY Algorithm Implementation**:
   - Bottom-up parsing
   - Maintains backpointers for tree reconstruction
   - Uses log probabilities for numerical stability

3. **Parse Tree Generation**:
   - Reconstructs trees from backpointer chart
   - Returns trees in Penn Treebank format
