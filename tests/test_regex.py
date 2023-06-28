import sys
import os


# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the module search path
sys.path.append(parent_dir)

from automata import DFA
from re_to_dfa.regex import Regex
from re_to_dfa.syntaxtree import SyntaxTree


def build_regex(string: str):
    return Regex(string)


def build_syntaxt_tree(regex: str):
    return SyntaxTree(regex)


def build_dfa(tree: SyntaxTree):
    return DFA().from_syntax_tree(tree)


print("------------ REGULAR EXPRESSION TO DFA -------------")

r = "(a|b)*abb"
rgx = build_regex(r)
tree = build_syntaxt_tree(rgx.get_regex())
dfa = build_dfa(tree)

print("Regular Expression: ", r)
print(dfa)
print(repr(dfa))

print("---------- SENTENCE RECOGNIZER -----------")

print(dfa.recognize_sentence("abb"))
print(dfa.recognize_sentence("abbb"))
print(dfa.recognize_sentence("bbaab"))
