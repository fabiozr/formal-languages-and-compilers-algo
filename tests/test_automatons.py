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


def assertEqual(a, b):
    return a == b


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


print("-------------------- NFA ---------------------")

nfa = build_nfa(transitions)
nfa2 = build_nfa(transitions2)
expected_nfa1 = {
    "q0": {"a": {"q1", "q0"}, "b": {"q0"}},
    "q1": {"b": {"q2"}, "a": set()},
    "q2": {"b": set(), "a": set()},
}
expected_nfa2 = {
    "q0": {"a": {"q1"}, "b": {"q1"}},
    "q1": {"a": {"q0"}, "b": {"q2"}},
    "q2": {"a": {"q0", "q2"}, "b": {"q1"}},
}
print("Passou no teste unitário:", assertEqual(nfa.transitions, expected_nfa1))
print(nfa)
print(repr(nfa))


print("Passou no teste unitário:", assertEqual(nfa2.transitions, expected_nfa2))
print(nfa2)
print(repr(nfa2))

print("--------------- NFA to DFA ---------------------")

dfa = build_dfa(nfa)
dfa2 = build_dfa(nfa2)

print(dfa)
print(repr(dfa))

print(dfa2)
print(repr(dfa2))

print("------------- MINIMIZATION OF DFAs --------------")

minimized_dfa = dfa.minimize()
print(dfa)
print(repr(dfa))
