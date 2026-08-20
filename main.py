from ast import Lexer, Parser, Flattener


def run():
    with open("rules.txt", "r", encoding="utf-8") as f:
        ebnf = f.read()

    lexer = Lexer(ebnf)
    token_stream = lexer.tokenise()
    print("Token Stream Generated")

    parser = Parser(token_stream)
    ast = parser.parse_grammar()
    print("AST Generated")

    flattener = Flattener(ast)
    flat_ast = flattener.flatten_grammar()
    print("AST Flattened")

    print(flat_ast)


if __name__ == "__main__":
    run()


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
