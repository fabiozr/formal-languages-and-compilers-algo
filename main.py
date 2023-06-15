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

nfa = NFA().from_transition_function(transitions)
print(nfa)
print(repr(nfa))

dfa = nfa.to_dfa()
print(dfa)
print(repr(dfa))

regular_grammar = dfa.to_regular_grammar().replace_symbols()
print(regular_grammar)
print(repr(regular_grammar))
