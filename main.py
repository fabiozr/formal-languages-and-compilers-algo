from automata import NFA, Transitions

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
    "*q2": {
        "a": {"q0", "q2"},
        "b": {"q1"}
        },
}

nfa = NFA().from_transition_function(transitions)
nfa2 = NFA().from_transition_function(transitions2)
print(nfa)
print(repr(nfa))

dfa = nfa.to_dfa()
dfa2 = nfa2.to_dfa()
print(dfa)
print(dfa2)
print(repr(dfa))
print(repr(dfa2))

# minimized automaton
dfa.minimize()
print(dfa)
print(repr(dfa))


print(dfa.union(dfa2))
print(dfa.intersection(dfa2))

regular_grammar = dfa.to_regular_grammar().replace_symbols()
print(regular_grammar)
print(repr(regular_grammar))
