from typing import Set, Union
from tabulate import tabulate
from abc import ABC, abstractmethod
from .constants import START, FINAL
from .types import Symbol, State, Transitions


class Automaton(ABC):
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
        self, state: State, symbol: Symbol, next_states: Set[State]
    ) -> None:
        if state not in self.transitions:
            self.transitions[state] = {}

        if symbol not in self.transitions[state]:
            self.transitions[state][symbol] = set()

        self.transitions[state][symbol] |= next_states

    def move(self, state: State, symbol: Symbol):
        return self.transitions.get(state, {}).get(symbol, set())

    def from_transition_function(self, transition_function: Transitions):
        known_states: Set[State] = set()
        for state, transitions in transition_function.items():
            parsed_state = state.replace(START, "").replace(FINAL, "")
            if START in state:
                self.initial_state = parsed_state
            if FINAL in state:
                self.final_states.add(parsed_state)

            known_states.add(parsed_state)
            for symbol, next_states in transitions.items():
                self.add_transition(parsed_state, symbol, next_states)

        for state in known_states:
            for symbol in self.alphabet:
                self.add_transition(state, symbol, set())

        for state in self.states:
            for symbol in self.alphabet:
                for next_state in self.move(state, symbol):
                    for symbol in self.alphabet:
                        self.add_transition(next_state, symbol, set())

        self._complete_transitions()
        return self.validate()

    def replace_states(self, state_letter: str = "q"):
        states = [f"{state_letter}{i}" for i in range(len(self.states))]
        old_states = sorted(
            self.states, key=lambda state: (state != self.initial_state)
        )
        new_states = dict(zip(old_states, states))

        self.initial_state = (
            new_states.get(self.initial_state) if self.initial_state else None
        )
        self.final_states = {new_states[state] for state in self.final_states}
        self._transitions = {
            new_states[state]: {
                symbol: {new_states[next_state] for next_state in next_states}
                for symbol, next_states in transitions.items()
            }
            for state, transitions in self.transitions.items()
        }

        return self.validate()

    def _complete_transitions(self):
        for state in self.states:
            for symbol in self.alphabet:
                for next_state in self.move(state, symbol):
                    for symbol in self.alphabet:
                        self.add_transition(next_state, symbol, set())
                self.add_transition(state, symbol, set())

    def validate(self):
        self._complete_transitions()

        for state in self.states:
            for symbol in self.alphabet:
                if not self.move(state, symbol).issubset(self.states):
                    raise Exception(
                        f"A next state {self.move(state, symbol)} is not in the states."
                    )

                if symbol not in self.transitions[state]:
                    raise Exception(f"Symbol {symbol} is not set for state {state}.")

        for final_state in self.final_states:
            if final_state not in self.states:
                raise Exception(f"Final state {final_state} is not in the states.")

        if self.initial_state and self.initial_state not in self.states:
            raise Exception(f"Initial state {self.initial_state} not in the states.")

        return self

    @abstractmethod
    def recognize_sentence(self, sentence: str) -> bool:
        pass
