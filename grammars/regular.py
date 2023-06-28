from .grammar import Grammar


class RegularGrammar(Grammar):
    def __init__(self):
        super().__init__()

    # (b.2) Conversão de GR para AFND
    def to_nfa(self):
        from automata import NFA

        nfa = NFA()

        nfa.initial_state = self.initial_symbol

        accepted_state = "X"

        for non_terminal, productions in self.productions.items():
            for production in productions:
                if len(production) == 1:
                    symbol = production[0]
                    nfa.add_transition(non_terminal, symbol, {accepted_state})
                elif len(production) == 2:
                    symbol = production[0]
                    next_non_terminal = production[1]
                    nfa.add_transition(non_terminal, symbol, {next_non_terminal})

        nfa.final_states.add(accepted_state)
        return nfa.validate()

    def validate(self):
        for productions in self.productions.values():
            for production in productions:
                if not (1 <= len(production) <= 2):
                    raise Exception(
                        f"Regular grammar production must have one or two symbols. Got {production}."
                    )
                if production[0] not in self.terminals:
                    raise Exception(
                        f"Regular grammar production must start with a terminal symbol. Got {production}."
                    )
                if len(production) == 2 and production[1] not in self.non_terminals:
                    raise Exception(
                        f"Regular grammar production of size 2 must end with a non terminal symbol. Got {production}."
                    )

        return super().validate()
