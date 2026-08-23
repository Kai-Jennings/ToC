from language import Engine

if __name__ == "__main__":
    engine = Engine("input")
    print(engine.parse(list("λx.λy.λz.xyz"), debug=True))

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
