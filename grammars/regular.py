from .grammar import Grammar


class RegularGrammar(Grammar):
    def __init__(self):
        super().__init__()

    # (b.2) Conversão de GR para AFN
    def to_nfa(self):
        raise NotImplementedError
