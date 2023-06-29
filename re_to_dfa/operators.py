SIMBOLS = {x: int(1e5) + i for i, x in enumerate("$#()[]")}

OPERATORS = {x: int(1.1e5) + i for i, x in enumerate("+?.|*")}

OPSMB = {**OPERATORS, **SIMBOLS}
