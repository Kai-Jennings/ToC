## To Do List
* [x] Reduce all multi-character terminals to a single character and concatenate to allow for single character parsing.
  * `rule = "terminal";` becomes `rule = "t", "e", "r", "m", "i", "n", "a", "l";`
* Optimise nested grouping AST generation.
  * Currently `rule = "a", ("a", ("a", ("a")));` generates `Rule(rule = Concat([Term(a), Concat([Term(a), Concat([Term(a), Term(a)])])]))`. Should instead produce `Rule(rule = Concat([Term(a), Term(a), Term(a), Term(a)]))`
  * Similarly `rule = "a" | ("b" | ("c" | ("d")));` generates:
      ```
      Rule(autogen_1 = Or([Term(c), Term(d)]))
      Rule(autogen_2 = Or([Term(b), ID('autogen_1')]))
      Rule(rule = Or([Term(a), ID('autogen_2')]))
      ```
    but instead should just generate `Rule(rule = Or([Term(a), Term(b), Term(c), Term(d)]))`
* Optimise rules that point to a single thing (remove reduntant rules).
  * Eg `rule = { "a" };` generates:
      ```
      Rule(autogen_1 = Or([Concat([Term(a), ID('autogen_1')]), Epsilon()]))
      Rule(rule = ID('autogen_1'))
      ```
    but instead should just generate `Rule(rule = Or([Concat([Term(a), ID('rule')]), Epsilon()]))`
  * Identical case above with `rule = [ "a" ];`
  * Could potentially substitute and remove rules that only point to a single `ID`/`TERM`
    * Eg
      ```
      rule = thing;
      thing = "a";
      ```
      could simply produce `Rule(rule = Term(a))`
* Allow EBNF parser to accept `"` terminals with `'"'` notation.
* Probably MANY more AST generation optimisations.
* Better error handling for basically every stage of the pipeline as there is currently barely any and the program will crash or hang with bad input.
* Better logging for the certain stages instead of bundling everything together and only having detailed logs for the final parsing.
  * For example you may want to see the AST of a language that isn't LL(1) but currently that will exit the program since we cannot parse it.
  * Goes hand in hand with making it more user friendly, since its currently kind of janky.
* Potentially add support for more EBNF syntactic sugar such as `+`, `-` and `*`.
* [x] MY TOC REPORT
