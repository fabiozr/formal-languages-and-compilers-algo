from typing import Set, List, Union
from tabulate import tabulate
from abc import ABC
from .types import Terminal, NonTerminal, Productions
from .constants import START


class Grammar(ABC):
    def __init__(self) -> None:
        self.initial_symbol: NonTerminal = START

        self._productions: Productions = {}

    def __str__(self):
        non_terminals = sorted(
            sorted(self.non_terminals),
            key=lambda x: (self.initial_symbol not in x, x[0]),
        )

        table = [["Non Terminal", "Productions"]]
        for non_terminal in non_terminals:
            row = [non_terminal]
            productions = " | ".join(
                [
                    " ".join(production)
                    for production in sorted(
                        self.productions[non_terminal],
                        key=lambda x: (
                            any(symbol != self.initial_symbol for symbol in x),
                            x[0],
                        ),
                    )
                ]
            )
            row.append(productions)
            table.append(row)

        return tabulate(table, headers="firstrow", tablefmt="fancy_grid")

    def __repr__(self) -> str:
        return f"Grammar(\n non_terminals={self.non_terminals},\n terminals={self.terminals},\n initial_symbol={self.initial_symbol},\n productions={self.productions}\n)"

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
        if production in self.productions.get(non_terminal, []):
            return
        if non_terminal not in self.non_terminals:
            self.productions[non_terminal] = [[]]
        else:
            self.productions[non_terminal].append([])

        for symbol in production:
            self.productions[non_terminal][-1].append(symbol)

    def replace_non_terminals(self):
        chars = [chr(i) for i in range(ord("A"), ord("Z") + 1) if chr(i) != "S"]
        symbols = [START] + chars
        non_terminals = sorted(
            sorted(list(self.non_terminals)), key=lambda x: (x != self.initial_symbol)
        )
        non_terminal_map = dict(
            zip(
                non_terminals,
                symbols,
            )
        )

        self.initial_symbol = non_terminal_map[self.initial_symbol]
        self._productions = {
            non_terminal_map[non_terminal]: [
                [
                    non_terminal_map[symbol] if symbol in non_terminal_map else symbol
                    for symbol in production
                ]
                for production in productions
            ]
            for non_terminal, productions in self.productions.items()
        }

        return self.validate()

    def validate(self):
        if self.initial_symbol not in self.non_terminals:
            raise Exception("Initial symbol is not in non terminals")

        return self
