from typing import Dict, List, Union

# Simbolo dos terminais Σ
Terminal = str

# Simbolo dos não terminais N
NonTerminal = str

# Produções P : N → (N ∪ Σ)*
Productions = Dict[NonTerminal, List[List[Union[Terminal, NonTerminal]]]]
