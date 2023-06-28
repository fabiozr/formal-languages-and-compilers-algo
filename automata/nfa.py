from typing import Set
from .automaton import Automaton
from .constants import EPSILON
from .types import State
from .dfa import DFA


class NFA(Automaton):
    def __init__(self) -> None:
        super().__init__()

    def epsilon_closure(self, state: State) -> Set[State]:
        closure: Set[State] = {state}
        for next_state in self.move(state, EPSILON):
            closure |= self.epsilon_closure(next_state)
        return closure

    def _states_to_str(self, state: Set[State]) -> str:
        return "{" + ", ".join(sorted(state)) + "}"

    # (a) Conversão de AFND (com e sem ε) para AFD
    def to_dfa(self):
        dfa = DFA()

        if self.initial_state is None:
            return dfa

        initial_epsilon_closure = self.epsilon_closure(self.initial_state)
        dfa.initial_state = self._states_to_str(initial_epsilon_closure)

        queue = [initial_epsilon_closure]
        while queue:
            current_states = queue.pop()
            current_states_str = self._states_to_str(current_states)

            for symbol in self.alphabet:
                if symbol == EPSILON:
                    continue
                next_states: Set[State] = set()

                for state in current_states:
                    for next_state in self.move(state, symbol):
                        next_states |= self.epsilon_closure(next_state)

                next_states_str = self._states_to_str(next_states)
                if next_states_str not in dfa.states:
                    queue.append(next_states)

                dfa.add_transition(current_states_str, symbol, {next_states_str})

        for state in dfa.states:
            for final_state in self.final_states:
                if final_state in state:
                    dfa.final_states.add(state)
        return dfa.validate()

    def recognize_sentence(self, sentence: str) -> bool:
        dfa = self.to_dfa()
        dfa.minimize()

        return dfa.recognize_sentence(sentence)
