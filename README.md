## Usage

Initialise an `Engine()` object with an argument of the name of the starting symbol (for ToC that will be `"input"`).
  ```
  engine = Engine("input")
  ```
  There is also one keyword argument:
  * `rule_file` (`str`) - Default: `"rules.txt"`. Overwrite if you wish to supply a different text file containing ebnf rules for a grammar. 

### Parsing
  To parse a string, call `Engine.parse()` with the string as an argument.
  ```
  engine.parse(string)
  ```
  There are also two keyword arguments:
  * `single_char_tokens` (`True`/`False`) - Default: `True`. Specifies whether to treat the input as a string (single character token stream) or a list of strings, for if you have a language with terminals that are more than a single character.
  * `debug` (`True`/`False`) - Default: `False`. Specifies whether to generate a logfile (`log.txt`) of the parsers actions as it is parsing.

### Generating
  To generate a random valid string from a given starting symbol, call `Engine.generate()` with the start symbol name as an argument.
  ```
  engine.generate("input") # Doesn't need to be the start symbol of the grammar, ie calling it with 'numeral' would generate random numbers etc.
  ```
  There is also one keyword argument:
  * `max_depth` (`int`) - Default: `15`. Specifies the maximum recursive depth of the walk before terminating routes will be chosen to exit as soon as possible.
