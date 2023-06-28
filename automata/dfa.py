from .constants import *
from .types import *
from .automaton import Automaton
from re_to_dfa.operators import *
from re_to_dfa.node import Node
from tabulate import tabulate


class DFA(Automaton):
    def __init__(self) -> None:
        super().__init__()

    def __str__(self):
        symbols = sorted(self.alphabet)
        states = sorted(self.states, key=lambda state: (state != self.initial_state))

        table = [[""] + symbols]
        for state in states:
            row = [state]
            if state == self.initial_state:
                row[0] = START + row[0]
            if state in self.final_states:
                row[0] = FINAL + row[0]
            for symbol in symbols:
                next_states = self.move(state, symbol)
                row.append("".join(next_states))
            table.append(row)

        return tabulate(table, tablefmt="fancy_grid")

    # (b.1) Conversão de AFD para GR
    def to_regular_grammar(self):
        from grammars import RegularGrammar

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

        return grammar.validate()

    # (c) Minimização de AFD
    def minimize(self):
        self._remove_unreachable_states()
        self._remove_dead_states()

        # Usando o algoritmo de Hopcroft
        P = [self.final_states, self.states - self.final_states]
        W = [self.final_states, self.states - self.final_states]
        while W:
            A = W.pop()
            for c in self.alphabet:
                X = {state for state in self.states if self.transitions[state][c] & A}
                for Y in P:
                    if X & Y and Y - X:
                        P.remove(Y)
                        P.append(X & Y)
                        P.append(Y - X)
                        if Y in W:
                            W.remove(Y)
                            W.append(X & Y)
                            W.append(Y - X)
                        else:
                            if len(X & Y) <= len(Y - X):
                                W.append(X & Y)
                            else:
                                W.append(Y - X)

        state_to_group = {}
        for group in P:
            for state in group:
                state_to_group[state] = str(group)

        self.initial_state = state_to_group[self.initial_state]
        self.final_states = {state_to_group[state] for state in self.final_states}
        self._transitions = {
            state_to_group[state]: {
                symbol: {state_to_group[list(next_state)[0]]}
                for symbol, next_state in transitions.items()
            }
            for state, transitions in self.transitions.items()
        }

        return self.validate()

    def _remove_unreachable_states(self):
        reachable_states: Set[State] = set(
            list(next_state)[0]
            for next_states in self.transitions.values()
            for next_state in next_states.values()
            if next_state
        )
        if self.initial_state:
            reachable_states.add(self.initial_state)

        self._transitions = {
            state: transition
            for state, transition in self.transitions.items()
            if state in reachable_states
        }

    def _remove_dead_states(self):
        uncheked_states = self.final_states.copy()
        alive_states = self.final_states.copy()

        while uncheked_states:
            final_state = uncheked_states.pop()
            for state in self.states:
                for _, next_state in self.transitions[state].items():
                    if (
                        next_state
                        and final_state == list(next_state)[0]
                        and state not in alive_states
                    ):
                        uncheked_states.add(state)
                        alive_states.add(state)

        self._transitions = {
            state: transitions
            for state, transitions in self.transitions.items()
            if state in alive_states
        }

    # (d.1) União de AFD
    def union(self, automata: "DFA"):
        from .nfa import NFA

        union_nfa = NFA()
        new_start_state = "q0"
        union_nfa.initial_state = new_start_state

        self.replace_states("p")
        if self.initial_state is not None:
            union_nfa.add_transition(new_start_state, EPSILON, {self.initial_state})
        for transition in self.transitions:
            union_nfa.transitions[transition] = self.transitions[transition]

        automata.replace_states("r")
        if automata.initial_state is not None:
            union_nfa.add_transition(new_start_state, EPSILON, {automata.initial_state})
        for transition in automata.transitions:
            union_nfa.transitions[transition] = automata.transitions[transition]

        union_nfa.final_states = self.final_states.union(automata.final_states)

        return union_nfa.validate()

    # (d.2) Interseção de AFD
    def intersection(self, automata: "DFA"):
        # Feito com base na lei de Morgan
        # L1 ∩ L2 = (L1' ∪ L2')'
        # A interseção de dois conjuntos é igual ao complemento da união dos complementos dos conjuntos
        first_automata_complement = self.complement()
        second_automata_complement = automata.complement()

        union_of_complements = first_automata_complement.union(
            second_automata_complement
        ).to_dfa()

        intersected_dfa = union_of_complements.complement().validate()

        return intersected_dfa

    def complement(self):
        complemented_dfa = DFA()
        complemented_dfa.initial_state = self.initial_state
        complemented_dfa.final_states = self.states - self.final_states
        complemented_dfa._transitions = self.transitions

        return complemented_dfa

    # (e) Diferença de AFD
    def from_syntax_tree(self, tree):
        dstates = [frozenset(tree.root.firstpos)]
        vis = set()
        statename = {}
        while dstates:
            state = dstates.pop()
            if state in vis:
                continue
            vis.add(state)
            statename.setdefault(state, f"q{len(statename)}")
            if any(Node.nodelist[i].v == SIMBOLS["#"] for i in state):
                self.final_states.add(state)
            for a in tree.symbols:
                z = set()
                for i in state:
                    node = Node.nodelist[i]
                    if node.v == a:
                        z |= node.followpos
                if len(z):
                    z = frozenset(z)
                    dstates.append(z)
                    self._transitions.setdefault(state, {})
                    if chr(a) not in OPSMB:
                        self._transitions[state][a] = z
                    else:
                        del self._transitions[state]

        initial_state = set()
        initial_state.add("q0")
        f_states = {statename[i] for i in self.final_states}

        transit = {
            statename[k1]: {
                chr(k2): statename[self._transitions[k1][k2]]
                for k2 in self._transitions[k1]
            }
            for k1 in self._transitions
        }
        for item in transit:
            for symbol in self.alphabet:
                set_value = set()
                value = transit[item][chr(symbol)]
                set_value.add(value)
                transit[item][chr(symbol)] = set_value

        self._transitions = transit
        self.initial_state = "q0"
        self.final_states = f_states

        return self

    def recognize_sentence(self, sentence: str) -> bool:
        if self.initial_state is None:
            return False

        current_state = self.initial_state
        for symbol in sentence:
            current_state = list(self.move(current_state, symbol))[0]
            if not current_state:
                return False
        return current_state in self.final_states

    def validate(self):
        super()._complete_transitions()
        for state, transitions in self.transitions.items():
            for symbol, next_states in transitions.items():
                if len(next_states) > 1:
                    raise Exception(
                        f"DFA next state must be a single state. For {state} -{symbol}-> Got: {next_states}"
                    )

        return super().validate()
