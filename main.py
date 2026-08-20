import re
from ast import Parser, Flattener

with open("rules.txt", "r", encoding="utf-8") as f:
    ebnf = f.read()


class Token:
    def __init__(self, _type, _value):
        self.type = _type
        self.value = _value


def tokenise(ebnf_str):
    tokens = []
    pointer = 0

    identifier_re = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    terminal_re = re.compile(r'"[^"]*"')
    operators = {'=', ',', '|', '{', '}', '[', ']', ';'}

    while pointer < len(ebnf_str):

        char = ebnf_str[pointer]

        if char.isspace():
            pointer += 1
            continue

        if char in operators:
            tokens.append(Token("OPERATOR", char))
            pointer += 1
            continue

        terminal_match = terminal_re.match(ebnf_str, pointer)
        if terminal_match:
            tokens.append(Token("TERMINAL", terminal_match.group(0)))
            pointer = terminal_match.end()
            continue

        identifier_match = identifier_re.match(ebnf_str, pointer)
        if identifier_match:
            tokens.append(Token("IDENTIFIER", identifier_match.group(0)))
            pointer = identifier_match.end()
            continue

    return tokens


# print("\n".join(f"{x.type:<12}{x.value:<10}" for x in tokenise(ebnf)))
tokens = tokenise(ebnf)
parser = Parser(tokens)
flattener = Flattener()
print(flattener.flatten_grammar(parser.parse_grammar()))


"""
input = { " " } , expression , { " " } ;

<input> -> <autogen1><expression><autogen2><empty space>

<autogen1> -> <" "><autogen1>
<autogen1> -> <empty space>
<autogen2> -> <" "><autogen2>
<autogen2> -> <empty space>

variable = letter , { letter | digit | "-" } ;

<variable> -> <letter><autogen3><empty space>
<autogen3> -> <letter><autogen3>
<autogen3> -> <digit><autogen3>
<autogen3> -> <"-"><autogen3>
<autogen3> -> <empty space>

"""
