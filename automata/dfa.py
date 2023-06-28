from automata.constants import *
from automata.types import *
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
    def union(self, automata: "DFA") -> "DFA":
        # Create a new DFA for the union
        union_dfa = DFA()
        union_alphabet = self.alphabet.union(automata.alphabet)
        union_transitions: Transitions = {}
        union_final_states = set[str]()
        union_start_state = "".join(self.initial_state) + "".join(
            automata.initial_state
        )
        # Add states from dfa1 and dfa2 to the union DFA
        for state1 in self.states:
            for state2 in automata.states:
                state1_str = "".join(state1)
                state2_str = "".join(state2)
                union_state_str = state1_str + state2_str
                union_transitions.setdefault(union_state_str, {})
                for symbol in union_alphabet:
                    transition1 = self.transitions[state1].get(symbol)
                    transition2 = automata.transitions[state2].get(symbol)
                    if state1 in self.final_states or state2 in automata.final_states:
                        union_final_states.add(union_state_str)
                    next_state_set = set()
                    t1_str = "".join(transition1)
                    t2_str = "".join(transition2)
                    t_value = t1_str + t2_str
                    next_state_set.add(t_value)
                    union_transitions[union_state_str][symbol] = next_state_set

        union_dfa.initial_state = "".join(union_start_state)
        union_dfa.final_states = union_final_states
        union_dfa._transitions = union_transitions

        return self

    # (d.2) Interseção de AFD
    def intersection(self, automata: "DFA") -> "DFA":
        intersected_dfa = DFA()
        intersected_final_states = set()
        intersected_start_state = set()
        initial_state = "".join(self.initial_state) + "".join(automata.initial_state)
        intersected_start_state.add(initial_state)
        intersected_alphabet = self.alphabet.intersection(automata.alphabet)
        intersected_transitions = {}

        for state1 in self.states:
            for state2 in automata.states:
                state1_str = "".join(state1)
                state2_str = "".join(state2)
                intersected_state_str = state1_str + state2_str
                intersected_transitions.setdefault(intersected_state_str, {})
                for symbol in intersected_alphabet:
                    transition1 = self.transitions[state1].get(symbol)
                    transition2 = automata.transitions[state2].get(symbol)
                    if state1 in self.final_states and state2 in automata.final_states:
                        intersected_final_states.add(intersected_state_str)
                    t_set = set()
                    t1_str = "".join(transition1)
                    t2_str = "".join(transition2)
                    t_value = t1_str + t2_str
                    t_set.add(t_value)
                    intersected_transitions[intersected_state_str][symbol] = t_set

        intersected_dfa.initial_state = "".join(intersected_start_state)
        intersected_dfa.final_states = intersected_final_states
        intersected_dfa._transitions = intersected_transitions

        return intersected_dfa

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
