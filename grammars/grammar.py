from typing import Set, List, Union
from tabulate import tabulate
from .types import Terminal, NonTerminal, Productions
from .constants import START


class Grammar:
    def __init__(self) -> None:
        self.initial_symbol: NonTerminal = START

        self._productions: Productions = {}

    def __str__(self):
        non_terminals = sorted(
            sorted(self.non_terminals), key=lambda x: (x != self.initial_symbol)
        )

        table = [["Symbols", "Productions"]]
        for non_terminal in non_terminals:
            row = [non_terminal]
            productions = " | ".join(
                [
                    " ".join(production)
                    for production in sorted(self.productions[non_terminal])
                ]
            )
            row.append(productions)
            table.append(row)

        return tabulate(table, headers="firstrow", tablefmt="fancy_grid")

    def __repr__(self) -> str:
        return f"Grammar(\n non_terminals={self.non_terminals},\n terminals={self.terminals},\n initial_symbol={self.initial_symbol},\n productions={self.productions}\n)"

    # TODO - add validation method for grammar

    @property
    def non_terminals(self) -> Set[NonTerminal]:
        return set(self._productions.keys())

    @property
    def terminals(self) -> Set[Terminal]:
        terminals: Set[Terminal] = set()

        for productions in self._productions.values():
            for production in productions:
                for symbol in production:
                    if symbol not in self.non_terminals:
                        terminals.add(symbol)

        return terminals

    @property
    def productions(self) -> Productions:
        return self._productions

    def add_production(
        self, non_terminal: NonTerminal, production: List[Union[Terminal, NonTerminal]]
    ) -> None:
        if non_terminal not in self.productions:
            self.productions[non_terminal] = [[]]
        else:
            self.productions[non_terminal].append([])

        for symbol in production:
            self.productions[non_terminal][-1].append(symbol)
