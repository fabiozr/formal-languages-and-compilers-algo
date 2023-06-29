from string import ascii_letters, digits, whitespace, printable
from .operators import *


class Regex:
    def __init__(self, regular_expression) -> None:
        self.regex = regular_expression
        self.run()

    def run(self):
        self.supercharge()
        self.opr_support()
        self.add_concat()
        self.infix_to_postfix()

    def supercharge(self):
        """Support advanced operators like +, ?, \\\\s, \\\\w, \\\\d ..."""

        def l(s):
            q = [SIMBOLS["("]]
            for i in s:
                q.append(ord(i))
                q.append(OPERATORS["|"])
            q.pop()
            q.append(SIMBOLS[")"])
            return q

        repl = {
            "\d": l(digits),
            "\s": l(whitespace),
            "\w": l(ascii_letters + digits + "_"),
            ".": l(printable.replace("\n", "")),
        }
        z = iter(self.regex)
        a = []
        for i in z:
            if i == "\\":
                i += next(z)
            if i in repl:
                a.extend(repl[i])
            elif i in OPSMB and i != "#":
                a.append(OPSMB[i])
            else:
                a.append(ord(i[-1]))

        self.regex = a

    def add_concat(self):
        """
        adds concat (.) operator to the regex\n
        (a|b)abb -> (a|b).a.b.b
        """
        z = [self.regex[0]]
        x, y = [OPERATORS["*"], SIMBOLS[")"], OPERATORS["|"]], [
            SIMBOLS["("],
            OPERATORS["|"],
        ]
        for i in range(1, len(self.regex)):
            if not (self.regex[i] in x or self.regex[i - 1] in y):
                z.append(OPERATORS["."])
            z.append(self.regex[i])
        z += [OPERATORS["."], SIMBOLS["#"]]

        self.regex = z

    def opr_support(self):
        """
        Support for optional(?) and kleene plus(+) operator\n
        -> converts ab?c to a(b|$)c ; ($ = epsilon)\n
        -> converts ab+c to abb*c
        """
        b = []
        for i in self.regex:
            if i != OPERATORS["?"] and i != OPERATORS["+"]:
                b.append(i)
            else:
                c, j = 0, []
                while b:
                    j.append(b.pop())
                    if j[-1] == SIMBOLS["("]:
                        c += 1
                    if j[-1] == SIMBOLS[")"]:
                        c -= 1
                    if c == 0:
                        break
                if not j or c != 0:
                    raise Exception("Invalid")
                j.reverse()
                b.append(SIMBOLS["("])
                b.extend(j)
                if i == OPERATORS["?"]:
                    b += [OPERATORS["|"], SIMBOLS["$"]]
                else:  # +
                    b.extend(j)
                    b.append(OPERATORS["*"])
                b.append(SIMBOLS[")"])

        self.regex = b

    def infix_to_postfix(self) -> list[int]:  # shunting yard
        # p={'*':3,'|':2,'.':1} # precedence
        opr, out = [], []
        z = {OPERATORS["*"], OPERATORS["."], OPERATORS["|"]}
        for c in self.regex:
            if c in z:
                while opr and opr[-1] != SIMBOLS["("] and opr[-1] >= c:
                    out.append(opr.pop())
                opr.append(c)
            elif c == SIMBOLS["("]:
                opr.append(c)
            elif c == SIMBOLS[")"]:
                while opr and opr[-1] != SIMBOLS["("]:
                    out.append(opr.pop())
                if not opr or opr.pop() != SIMBOLS["("]:
                    raise Exception("Invalid")
            else:
                out.append(c)
        while opr:
            if opr[-1] == SIMBOLS["("]:
                raise Exception("Invalid")
            out.append(opr.pop())

        self.regex = out

        return self.regex

    def get_regex(self):
        return self.regex
