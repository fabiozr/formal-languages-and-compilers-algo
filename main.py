from automata import NFA, Transitions, DFA
from re_to_dfa.regex import *
from re_to_dfa.syntaxtree import SyntaxTree

transitions: Transitions = {
    "→q0": {
        "a": {"q0", "q1"},
        "b": {"q0"},
    },
    "q1": {
        "b": {"q2"},
    },
    "*q2": {},
}

transitions2: Transitions = {
    "→q0": {
        "a": {"q1"},
        "b": {"q1"},
    },
    "q1": {
        "a": {"q0"},
        "b": {"q2"},
    },
    "*q2": {"a": {"q0", "q2"}, "b": {"q1"}},
}

print("-------------------- NFA ---------------------")

nfa = NFA().from_transition_function(transitions)
nfa2 = NFA().from_transition_function(transitions2)
print(nfa)
print(repr(nfa))
print(nfa.recognize_sentence("ab"))

print("-------------------- NFA TO DFA ---------------------")

dfa = nfa.to_dfa()
print(dfa)
print(repr(dfa))

print("-------------------- MINIMIZATION OF DFAs ---------------------")

dfa.minimize()
print(dfa)
print(repr(dfa))

print("-------------------- UNION/INTERSECTION OF DFAs ---------------------")

# TODO test the minimization after union or intersection
dfa2 = nfa2.to_dfa()
a = dfa.union(dfa2)
b = dfa.intersection(dfa2)
print(dfa.union(dfa2))

print(b.minimize())
print(dfa.intersection(dfa2))
print(dfa.intersection(dfa2).minimize())

print("-------------------- DFA TO RG / RG TO NFA ---------------------")

regular_grammar = dfa.to_regular_grammar().replace_symbols()
print(regular_grammar)
print(regular_grammar.to_nfa())
print(repr(regular_grammar))

print("-------------------- REGULAR EXPRESSION TO DFA ---------------------")

r = "(a|b)*abb"
print("Regular Expression: ", r)
rgx = Regex(r)
tree = SyntaxTree(rgx.get_regex())
a = DFA().from_syntax_tree(tree)
print(a)
print(repr(a))

print(a.recognize_sentence("abb"))

print("--------------------------------------------")
new_nfa = NFA()
print(regular_grammar)
print(repr(regular_grammar))
