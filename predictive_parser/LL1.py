from grammars import ContextFreeGrammar
from typing import Dict, Set, List
from grammars import NonTerminal, Terminal, Production
from tabulate import tabulate

EPSILON = "&"
END = "$"


class PredictiveParserLL1:
    def __init__(self):
        self.grammar: ContextFreeGrammar = ContextFreeGrammar()
        self.firsts: Dict[NonTerminal, Set[Terminal]] = {}
        self.follows: Dict[NonTerminal, Set[Terminal]] = {}
        self.table: Dict[NonTerminal, Dict[Terminal, Production]] = {}

    def __str__(self):
        columns = self.grammar.terminals | {END}
        columns = sorted(list(columns - {EPSILON}))

        rows = self.grammar.non_terminals
        rows = sorted(list(rows))
        table = []

        for row in rows:
            table_row = []
            for column in columns:
                if column in self.table[row]:
                    table_row.append(self.table[row][column])
                else:
                    table_row.append("")
            table.append(table_row)

        return tabulate(table, headers=columns, showindex=rows, tablefmt="fancy_grid")

    def __repr__(self):
        return f"PredictiveParserLL1(\n grammar={repr(self.grammar)},\n firsts={self.firsts},\n follows={self.follows},\n table={self.table}\n)"

    def from_grammar(self, grammar: ContextFreeGrammar) -> "PredictiveParserLL1":
        self.grammar = grammar
        self.firsts = self.grammar.firsts()
        self.follows = self.grammar.follows()

        for non_terminal in self.grammar.non_terminals:
            if (
                EPSILON in self.firsts[non_terminal]
                and non_terminal in self.follows[non_terminal]
            ):
                raise Exception(f"First({non_terminal}) ∩ Follow({non_terminal}) != ∅")

        self.table = self._build_table()
        return self

    def _build_table(self) -> Dict[NonTerminal, Dict[Terminal, Production]]:
        table: Dict[NonTerminal, Dict[Terminal, Production]] = {}
        for non_terminal, productions in self.grammar.productions.items():
            table[non_terminal] = {}
            for production in productions:
                for symbol in self.firsts[non_terminal]:
                    if symbol != EPSILON and production[0] != EPSILON:
                        table[non_terminal][symbol] = production
                if production[0] == EPSILON:
                    for symbol in self.follows[non_terminal]:
                        table[non_terminal][symbol] = production

        return table

    def parse(self, sentence: List[str]) -> List[Production]:
        stack: List[str] = [self.grammar.initial_symbol]
        productions: List[Production] = [[self.grammar.initial_symbol]]
        sentence.append(END)

        while stack:
            symbol = stack.pop()

            if symbol in self.grammar.terminals:
                if symbol == sentence[0]:
                    sentence = sentence[1:]
                else:
                    raise Exception("Could not parse sentence")
            elif symbol in self.grammar.non_terminals:
                production = self.table.get(symbol, {}).get(sentence[0], [])

                if not production:
                    raise Exception("Could not parse sentence")

                productions.append(production)

                if production[0] != EPSILON:
                    stack.extend(reversed(production))

            else:
                raise Exception("Could not parse sentence")

        return productions
