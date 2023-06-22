from .grammar import Grammar


class RegularGrammar(Grammar):
    def __init__(self):
        super().__init__()

    # (b.2) Conversão de GR para AFN
    def to_nfa(self, nfa):
        start_state = self.initial_symbol
        transitions = {}
        states = set()
        final_state = "END"
        transitions.setdefault(final_state, {})

        # Create states
        for non_terminal in self.non_terminals:
            states.add(non_terminal)
            transitions.setdefault(non_terminal, {})

        # Create transitions
        for state, productions in self._productions.items():
            for production in productions:
                if len(production) == 1:
                    symbol = production[0]
                    next_state = final_state
                    transitions[state].setdefault(symbol, set()).add(next_state)
                else:
                    symbol = production[0]
                    next_state = production[1]  # Convert to tuple
                    transitions[state].setdefault(symbol, set()).add(next_state)

        nfa.initial_state = start_state
        nfa.final_states = {final_state}
        nfa._transitions = transitions

        return nfa
