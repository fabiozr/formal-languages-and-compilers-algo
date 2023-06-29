import sys
import os


# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the module search path
sys.path.append(parent_dir)

from grammars import ContextFreeGrammar, RegularGrammar

# # E -> T E’
# # E’ -> + T E’
# # E’ -> ''
# # T -> F T’
# # T’ -> * F T’
# # T’ -> ''
# # F -> ( E )
# # F -> id
c = ContextFreeGrammar()
c.add_production("E", ["T", "E'"])
c.add_production("E'", ["+", "T", "E'"])
c.add_production("E'", ["&"])
c.add_production("T", ["F", "T'"])
c.add_production("T'", ["*", "F", "T'"])
c.add_production("T'", ["&"])
c.add_production("F", ["(", "E", ")"])
c.add_production("F", ["id"])
c.initial_symbol = "E"


a = ContextFreeGrammar()
# E::=E+T|E−T|T T ::=T ∗F |F |T/F
# F ::=F ∗∗P |P
# P ::=(E)|id|cte
a.add_production("E", ["E", "+", "T"])
a.add_production("E", ["E", "-", "T"])
a.add_production("E", ["T"])
a.add_production("T", ["T", "*", "F"])
a.add_production("T", ["F"])
a.add_production("T", ["T", "/", "F"])
a.add_production("F", ["F", "**", "P"])
a.add_production("F", ["P"])
a.add_production("P", ["(", "E", ")"])
a.add_production("P", ["id"])
a.add_production("P", ["cte"])
a.initial_symbol = "E"

a = a.remove_left_recursion()
print(a)
