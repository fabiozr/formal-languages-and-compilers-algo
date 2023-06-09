from .automaton import Automaton
from grammars import RegularGrammar


class DFA(Automaton):
    def __init__(self) -> None:
        super().__init__()

    # (b.1) Conversão de AFD para GR
    def to_regular_grammar(self) -> RegularGrammar:
        grammar = RegularGrammar()

        if self.initial_state is None:
            return grammar

        grammar.initial_symbol = self.initial_state

        for state in self.states:
            for symbol, next_state in self.transitions[state].items():
                next_state = list(next_state)[0]

                if next_state in self.final_states:
                    grammar.add_production(state, [symbol])
                grammar.add_production(state, [symbol, next_state])

        return grammar
