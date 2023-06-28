from .grammar import Grammar
from .constants import EPSILON, END
from typing import Dict, List, Set, Union
from .types import Production, NonTerminal, Terminal


class ContextFreeGrammar(Grammar):
    def __init__(self):
        super().__init__()

    # (h.2.1) verificação de não determinismo
    def has_direct_non_deterministic(self):
        for productions in self.productions.values():
            symbols_to_productions: Dict[Terminal, List[Production]] = {}
            for symbol in self.terminals:
                symbols_to_productions[symbol] = []

            for production in productions:
                symbol = production[0]
                if symbol in self.terminals:
                    symbols_to_productions[symbol].append(production)

            for symbol, productions in symbols_to_productions.items():
                if len(productions) > 1:
                    return True

        return False

    # (h.2.2) fatoração da gramática
    def remove_non_determinism(self, retries: int = 0) -> "ContextFreeGrammar":
        import json

        new_grammar = self._remove_direct_non_determinism()

        self_hash = hash(json.dumps(self.productions, sort_keys=True))
        new_grammar_hash = hash(json.dumps(new_grammar.productions, sort_keys=True))
        if self_hash == new_grammar_hash:
            return new_grammar.validate()

        if retries > 10:
            raise Exception("Could fully remove non determinism")

        return new_grammar.remove_non_determinism(retries + 1)

    def _remove_direct_non_determinism(self):
        new_grammar = ContextFreeGrammar()
        new_grammar.initial_symbol = self.initial_symbol

        for non_terminal, productions in self.productions.items():
            symbols_to_productions: Dict[Terminal, List[Production]] = {}
            for symbol in self.terminals:
                symbols_to_productions[symbol] = []

            for production in productions:
                symbol = production[0]
                if symbol in self.terminals:
                    symbols_to_productions[symbol].append(production)
                else:
                    new_grammar.add_production(non_terminal, production)

            for symbol, symbol_productions in symbols_to_productions.items():
                if len(symbol_productions) > 1:
                    new_non_terminal = f"{non_terminal}'"
                    while new_non_terminal in new_grammar.non_terminals:
                        new_non_terminal += "'"

                    new_grammar.add_production(non_terminal, [symbol, new_non_terminal])

                    for symbol_production in symbol_productions:
                        new_grammar.add_production(
                            new_non_terminal, symbol_production[1:]
                        )
                else:
                    for symbol_production in symbol_productions:
                        new_grammar.add_production(non_terminal, symbol_production)

        return new_grammar.validate()

    def _remove_indirect_non_determinism(self) -> "ContextFreeGrammar":
        new_grammar = ContextFreeGrammar()
        new_grammar.initial_symbol = self.initial_symbol

        for non_terminal, productions in self.productions.items():
            for production in productions:
                if production[0] in self.non_terminals:
                    for new_production in self.productions[production[0]]:
                        new_grammar.add_production(
                            non_terminal, new_production + production[1:]
                        )
                else:
                    new_grammar.add_production(non_terminal, production)
            if new_grammar.has_direct_non_deterministic():
                new_grammar = new_grammar._remove_direct_non_determinism()
                self = new_grammar
            else:
                new_grammar._productions[non_terminal] = productions
                self = new_grammar

        return new_grammar.validate()

    # (h.3) eliminação de recursão a esquerda // so funciona se a gramatica nao tiver & producao e unitario
    def remove_left_recursion(self):
        return self._remove_indirect_left_recursion()._remove_direct_left_recursion()

    def _remove_indirect_left_recursion(self):
        new_grammar = ContextFreeGrammar()
        new_grammar.initial_symbol = self.initial_symbol

        non_terminals = sorted(
            self.non_terminals, key=lambda x: x[0] != self.initial_symbol
        )
        for i in range(len(non_terminals)):
            for j in range(i):
                productions_i = self.productions[non_terminals[i]]
                productions_j = self.productions[non_terminals[j]]

                for production_i in productions_i:
                    if production_i[0] == non_terminals[j]:
                        for production_j in productions_j:
                            updated_production_i = production_j + production_i[1:]
                            new_grammar.add_production(
                                non_terminals[i], updated_production_i
                            )
                    else:
                        new_grammar.add_production(non_terminals[i], production_i)

        # productions_not_added = {
        #     non_terminal: productions
        #     for non_terminal, productions in self.productions.items()
        #     if non_terminal not in new_grammar.non_terminals
        # }

        # new_grammar._productions.update(productions_not_added)

        for non_terminal in non_terminals:
            if non_terminal not in new_grammar.non_terminals:
                for production in self.productions[non_terminal]:
                    new_grammar.add_production(non_terminal, production)

        return new_grammar.validate()

    def _remove_direct_left_recursion(self):
        new_grammar = ContextFreeGrammar()
        new_grammar.initial_symbol = self.initial_symbol
        for non_terminal, productions in self.productions.items():
            is_left_recursive = False
            for production in productions:
                if production[0] == non_terminal:
                    is_left_recursive = True
                    break
            if is_left_recursive:
                new_non_terminal = non_terminal + "'"
                for production in productions:
                    if production[0] == non_terminal:
                        new_grammar.add_production(
                            new_non_terminal, production[1:] + [new_non_terminal]
                        )
                    else:
                        new_grammar.add_production(
                            non_terminal, production + [new_non_terminal]
                        )
                new_grammar.add_production(new_non_terminal, [EPSILON])
            else:
                for production in productions:
                    new_grammar.add_production(non_terminal, production)
        return new_grammar.validate()

    # (h.4)  Firsts e Follows
    def firsts(self):
        firsts: Dict[Union[NonTerminal, Terminal], Set[Terminal]] = {}
        for non_terminal in self.non_terminals:
            firsts[non_terminal] = self._firsts(non_terminal)

        return firsts

    def _firsts(self, symbol: Union[NonTerminal, Terminal]) -> Set[Terminal]:
        firsts: Set[Terminal] = set()

        if symbol in self.terminals:
            firsts.add(symbol)
            return firsts

        for production in self.productions[symbol]:
            if production[0] in self.terminals:
                firsts.add(production[0])
            elif production[0] == EPSILON:
                firsts.add(EPSILON)
            elif production[0] in self.non_terminals:
                next_firsts = self._firsts(production[0])
                firsts.update(next_firsts - {EPSILON})
                if EPSILON in next_firsts:
                    i = 1
                    while i < len(production) and EPSILON in next_firsts:
                        next_firsts = self._firsts(production[i])
                        firsts.update(next_firsts - {EPSILON})
                        i += 1
                    if i == len(production) and EPSILON in next_firsts:
                        firsts.add(EPSILON)
        return firsts

    # (h.4)  Firsts e Follows
    def follows(self):
        import json

        table = self._follows({})
        table_hash = hash(json.dumps(str(table), sort_keys=True))
        test_hash = ""
        while table_hash != test_hash:
            test_hash = table_hash
            table = self._follows(table)
            table_hash = hash(json.dumps(str(table), sort_keys=True))

        return table

    def _follows(self, follow_table: Dict[NonTerminal, Set[Terminal]]):
        follows: Dict[NonTerminal, Set[Terminal]] = follow_table

        for non_terminal in self.non_terminals:
            if non_terminal not in follows:
                follows[non_terminal] = set()

        follows[self.initial_symbol].add(END)

        for non_terminal, productions in self.productions.items():
            for production in productions:
                for i in range(len(production)):
                    symbol = production[i]
                    next_symbol = production[i + 1] if i + 1 < len(production) else None
                    if symbol not in self.non_terminals:
                        continue
                    if next_symbol is None:
                        follows[symbol].update(follows[non_terminal])
                    if next_symbol:
                        next_firsts = self._firsts(next_symbol)
                        follows[symbol].update(next_firsts - {EPSILON})
                        if EPSILON in next_firsts:
                            test = next_firsts - {EPSILON} | follows[non_terminal]
                            follows[symbol].update(test)

        return follows
