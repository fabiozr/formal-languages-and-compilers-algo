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

    def replace_symbols(self):
        chars = [chr(i) for i in range(ord("A"), ord("Z") + 1) if chr(i) != "S"]
        symbols = [START] + chars
        non_terminals = sorted(
            sorted(list(self.non_terminals)), key=lambda x: (x != self.initial_symbol)
        )
        symbol_dict = dict(
            zip(
                non_terminals,
                symbols,
            )
        )

        new_productions: Productions = {}
        for non_terminal, productions in self.productions.items():
            new_productions[symbol_dict[non_terminal]] = []
            for production in productions:
                new_production: List[Union[Terminal, NonTerminal]] = []
                for symbol in production:
                    if symbol in symbol_dict:
                        new_production.append(symbol_dict[symbol])
                    else:
                        new_production.append(symbol)
                new_productions[symbol_dict[non_terminal]].append(new_production)

        self.initial_symbol = symbol_dict["".join(self.initial_symbol)]
        self._productions = new_productions

        return self
