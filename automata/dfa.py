from automata.constants import *
from automata.types import *
from utils.disjoint_set import DisjointSet
from .automaton import Automaton
from grammars import RegularGrammar
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
                next_states = self._transitions[state][symbol]
                row.append("".join(next_states))
            table.append(row)

        return tabulate(table, tablefmt="fancy_grid")

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

    def reachable_states(self) -> list[Set[State]]:
        return list(
            next_state
            for next_states in self.transitions.values()
            for next_state in next_states.values()
        )

    def minimize(self) -> None:
        self.remove_unreachable_states()
        self.remove_dead_states()
        table = {}
        final_states = self.final_states
        iterate = True
        states = [self.states]

        for i, state in enumerate(states):
            for state2 in states[1 + i :]:
                table[(state, state2)] = (state in final_states) != (
                    state2 in final_states
                )
        while iterate:
            iterate = False

            for i, state in enumerate(states):
                for state2 in states[i + 1 :]:
                    if table[(state, state2)]:
                        continue

                    # check if the states are distinguishable
                    for symbol in self.alphabet:
                        t1 = self.transitions[state][symbol]
                        t2 = self.transitions[state2][symbol]

                        if t1 != t2:
                            marked = table[list(t1)[0], list(t2)[0]]
                            iterate = iterate or marked
                            table[(state, state2)] = marked

                            if marked:
                                break

        d = DisjointSet(self.states)
        new_final_states = set()
        new_transitions = {}
        # form new states
        for k, v in table.items():
            if not v:
                d.union(k[0], k[1])

        # form new final states
        for s in d.get():
            for item in s:
                if item in self.final_states:
                    final_state = "".join(d.find(item))
                    new_final_states.add(final_state)
                    break

        # form new transitions
        for k, v in self.transitions.items():
            new_state = d.find(k)
            symbols = v.keys()
            if k in new_state:
                k = "".join(new_state)
            for symbol in symbols:
                aux = d.find(list(v[symbol])[0])
                v[symbol] = {"".join(aux)}
            new_transitions[k] = v

        self.initial_state = d.find(self.initial_state)
        if isinstance(self.initial_state, list):
            self.initial_state = "".join(self.initial_state)
        self._transitions = new_transitions
        self.final_states = new_final_states
        return self

    def remove_unreachable_states(self):
        next_states = self.reachable_states()
        reachable_states = set()
        if isinstance(self.initial_state, set):
            init_state = "".join(self.initial_state)
            reachable_states.add(init_state)

        for state in next_states:
            state_str = "".join(state)
            reachable_states.add(state_str)

        self._transitions = {
            k: v for k, v in self.transitions.items() if k in reachable_states
        }

        self.remove_unreachable_transitions()

    def remove_dead_states(self):
        start = list(self.final_states)
        alive_states = set(start)

        while start:
            final_state = start.pop()
            for state in self.states:
                for _, next_state in self.transitions[state].items():
                    if final_state == list(next_state)[0] and state not in alive_states:
                        start.append(state)
                        alive_states.add(state)

        self._transitions = {
            k: v for k, v in self.transitions.items() if k in alive_states
        }

        self.remove_unreachable_transitions()

    def remove_unreachable_transitions(self):
        keys_to_remove = []
        for k, v in self._transitions.items():
            keys_to_remove.extend(
                (k, key)
                for key, element in v.items()
                if list(element)[0] not in self.states
            )

        for k, key in keys_to_remove:
            del self._transitions[k][key]

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
