from language import Lexer, Parser, Flattener, FirstSet, FollowSet, ParseTable, LL1Parser


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

    first_calc = FirstSet(flat_ast)
    first_sets = first_calc.calculate()
    print("First Sets Generated")

    follow_calc = FollowSet(flat_ast, first_calc, "input")
    follow_sets = follow_calc.calculate()
    print("Follow Sets Generated")

    table_gen = ParseTable(flat_ast, first_calc, follow_sets)
    ll1_table = table_gen.generate()
    print("Generated LL(1) Parse Table")

    ll1_parser = LL1Parser(ll1_table, debug=True)
    print(ll1_parser.parse(list("λx.λy.λz.xyz"), "input"))


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
