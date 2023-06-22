from typing import Set
from .dfa import DFA
from .automaton import Automaton
from .constants import EPSILON
from .types import State


class NFA(Automaton):
    def __init__(self) -> None:
        super().__init__()

    def epsilon_closure(self, state: State) -> Set[State]:
        closure: Set[State] = {state}
        for next_state in self.move(state, EPSILON):
            closure |= self.epsilon_closure(next_state)
        return closure

    def state_to_str(self, state: Set[State]) -> str:
        return "{" + ", ".join(sorted(state)) + "}"

    # (a) Conversão de AFND (com e sem ε) para AFD
    def to_dfa(self) -> DFA:
        dfa = DFA()

        if self.initial_state is None:
            return dfa

        initial_epsilon_closure = self.epsilon_closure(self.initial_state)
        dfa.initial_state = self.state_to_str(initial_epsilon_closure)

        queue = [initial_epsilon_closure]
        while queue:
            current_states = queue.pop()
            current_states_str = self.state_to_str(current_states)

            for symbol in self.alphabet:
                next_states: Set[State] = set()

                for state in current_states:
                    for next_state in self.move(state, symbol):
                        next_states |= self.epsilon_closure(next_state)

                next_states_str = self.state_to_str(next_states)
                if next_states_str not in dfa.states:
                    queue.append(next_states)

                dfa.add_transition(current_states_str, symbol, {next_states_str})

        for state in dfa.states:
            for final_state in self.final_states:
                if final_state in state:
                    dfa.final_states.add(state)
        return dfa

    def recognize_sentence(self, sentence: str) -> bool:
        dfa = self.to_dfa()
        dfa.minimize()

        if dfa.initial_state is None:
            return False
        current_state = dfa.initial_state

        for char in sentence:
            if char not in dfa.alphabet:
                return False
            current_state_str: str = "".join(current_state)
            current_state = dfa.transitions[current_state_str].get(char)
            if current_state is None:
                return False
        current_state_str = "".join(current_state)

        return current_state_str in dfa.final_states
