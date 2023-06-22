from typing import Set, Union
from tabulate import tabulate
from .constants import START, FINAL
from .types import Symbol, State, Transitions


class Automaton:
    def __init__(self) -> None:
        self.initial_state: Union[State, None] = None
        self.final_states: Set[State] = set()

        self._transitions: Transitions = {}

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
                next_states = sorted(self.move(state, symbol))
                row.append(", ".join(next_states))
            table.append(row)

        return tabulate(table, tablefmt="fancy_grid")

    def __repr__(self) -> str:
        return f"Automaton(\n states={self.states},\n alphabet={self.alphabet},\n initial_state={self.initial_state},\n final_states={self.final_states},\n transitions={self.transitions}\n)"

    # TODO - add validation method for automaton

    @property
    def states(self) -> Set[State]:
        return set(self.transitions.keys())

    @property
    def alphabet(self) -> Set[Symbol]:
        return set(
            symbol for symbols in self.transitions.values() for symbol in symbols.keys()
        )

    @property
    def transitions(self) -> Transitions:
        return self._transitions

    def add_transition(
        self, state: State, symbol: Symbol, next_state: Set[State]
    ) -> None:
        if state not in self.transitions:
            self.transitions[state] = {}

        if symbol not in self.transitions[state]:
            self.transitions[state][symbol] = set()

        self.transitions[state][symbol] = next_state

    def move(self, state: State, symbol: Symbol) -> Set[State]:
        return self.transitions.get(state, {}).get(symbol, set())

    def from_transition_function(self, transition_function: Transitions):
        for state, transitions in transition_function.items():
            parsed_state = state.replace(START, "").replace(FINAL, "")

            if START in state:
                self.initial_state = parsed_state
            if FINAL in state:
                self.final_states.add(parsed_state)

            for symbol, next_states in transitions.items():
                self.add_transition(parsed_state, symbol, next_states)

        return self

    def recognize_sentence(self, sentence: str) -> bool:
        if self.initial_state is None:
            return False
        current_state = self.initial_state

        for char in sentence:
            if char not in self.alphabet:
                return False
            current_state_str: str = "".join(current_state)
            current_state = self.transitions[current_state_str].get(char)
            if current_state is None:
                return False
        current_state_str = "".join(current_state)

        return current_state_str in self.final_states
