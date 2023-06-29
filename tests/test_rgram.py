import sys
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the module search path
sys.path.append(parent_dir)

from automata import NFA, Transitions


def build_nfa(transition: Transitions):
    nfa = NFA()
    return nfa.from_transition_function(transition)


def build_dfa(nfa: NFA):
    dfa = nfa.to_dfa()
    return dfa


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


print("----------- DFA TO RG  ---------------")

nfa = build_nfa(transitions)
nfa2 = build_nfa(transitions2)
dfa = build_dfa(nfa)
dfa2 = build_dfa(nfa2)

regular_grammar = dfa.to_regular_grammar()
regular_grammar2 = dfa2.to_regular_grammar()
print(dfa)
print(regular_grammar)
print(repr(regular_grammar))

print("----------- RG TO DFA  ---------------")

print(regular_grammar2)
print(dfa2)
print(repr(regular_grammar2))

print("----------- RG TO NFA  ---------------")

print(regular_grammar.to_nfa())
print(nfa)
print(regular_grammar2.to_nfa())
print(nfa2)
