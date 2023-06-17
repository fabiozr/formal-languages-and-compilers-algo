from utils.disjoint_set import DisjointSet
from .automaton import Automaton
from grammars import RegularGrammar


class DFA(Automaton):
    def __init__(self) -> None:
        super().__init__()

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

    def minimize(self) -> None:
        self.remove_unreachable_states()
        self.remove_dead_states()

        table = {}

        final_states = self.final_states
        interate = True
        states = sorted(self.states)

        for i, state in enumerate(states):
            for state2 in states[1 + i :]:
                table[(state, state2)] = (state in final_states) != (
                    state2 in final_states
                )
        while interate:
            interate = False

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
                            interate = interate or marked
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

        self.initial_state = "".join(d.find(self.initial_state))
        self._transitions = new_transitions
        self.final_states = new_final_states

    def remove_unreachable_states(self):
        reachable_states = set()

        start = [self.initial_state]

        while start:
            state = start.pop()

            if state not in reachable_states:
                for _, next_state in self.transitions[state].items():
                    start += next_state
            reachable_states.add(state)

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
