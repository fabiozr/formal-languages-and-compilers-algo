import sys
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the module search path
sys.path.append(parent_dir)

from automata import NFA, Transitions, DFA

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


def build_nfa(transition: Transitions):
    nfa = NFA()
    return nfa.from_transition_function(transition)


def build_dfa(nfa: NFA):
    dfa = nfa.to_dfa()
    return dfa


def minimize_dfa(dfa: DFA):
    return dfa.minimize()


def union_dfa(dfa1: DFA, dfa2: DFA):
    return dfa.union(dfa2)


def intersection_dfa(dfa1: DFA, dfa2: DFA):
    return dfa.union(dfa2)


print("--------- UNION/INTERSECTION OF DFAs ------------")

nfa = build_nfa(transitions)
nfa2 = build_nfa(transitions2)

dfa = build_dfa(nfa)
dfa2 = build_dfa(nfa2)


union = union_dfa(dfa, dfa2)
intersection = intersection_dfa(dfa, dfa2)

print(union)
print(repr(union))

print(intersection)
print(repr(intersection))
