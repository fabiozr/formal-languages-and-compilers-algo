import sys
import os


# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the module search path
sys.path.append(parent_dir)

from grammars import ContextFreeGrammar
from predictive_parser.LL1 import PredictiveParserLL1

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

parser = PredictiveParserLL1().from_grammar(c)
print(parser)

sentences = [
    ["id", "+", "id", "*", "id"],
    ["id", "+", "id", "*", "id", "+", "id"],
    ["id", "+", "id", "*", "id", "+", "id", "*", "id"],
]

for sentence in sentences:
    result = parser.parse(sentence)
    print(result)
