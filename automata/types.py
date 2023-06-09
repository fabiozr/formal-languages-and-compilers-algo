from typing import Dict, Set

# Simbolo do alfabeto Σ
Symbol = str

# Estado do autômato Q
State = str

# Função de transição δ : Q × Σ → P(Q)
Transitions = Dict[State, Dict[Symbol, Set[State]]]
