from typing import Dict, List, Union

# Simbolo dos terminais Σ
Terminal = str

# Simbolo dos não terminais N
NonTerminal = str

# Produções P : N → (N ∪ Σ)*
Production = List[Union[Terminal, NonTerminal]]
Productions = Dict[NonTerminal, List[Production]]
