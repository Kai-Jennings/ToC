from re import compile


class Token:
    def __init__(self, _type, _value):
        self.type = _type
        self.value = _value

    def __repr__(self):
        return f"({self.type}: {self.value})"


class Node:
    pass


class GrammarNode(Node):
    def __init__(self, children):
        self.children = children

    def __repr__(self):
        return "Grammar:\n " + "\n ".join(str(x) for x in self.children)


class RuleNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Rule({self.left} = {self.right})"


class OrNode(Node):
    def __init__(self, children):
        self.children = children

    def __repr__(self):
        return f"Or({self.children})"


class ConcatenationNode(Node):
    def __init__(self, children):
        self.children = children

    def __repr__(self):
        return f"Concat({self.children})"


class IdentifierNode(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"ID('{self.value}')"


class TerminalNode(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Term({self.value})"


class RepeatNode(Node):
    def __init__(self, inner):
        self.inner = inner

    def __repr__(self):
        return f"Repeat({self.inner})"


class OptionalNode(Node):
    def __init__(self, inner):
        self.inner = inner

    def __repr__(self):
        return f"Optional({self.inner})"


class GroupingNode(Node):
    def __init__(self, inner):
        self.inner = inner

    def __repr__(self):
        return f"Group({self.inner})"


class EpsilonNode(Node):
    def __repr__(self):
        return "Epsilon()"


class Lexer:
    def __init__(self, ebnf_str):
        self.ebnf_str = ebnf_str
        self.token_stream = []
        self.pointer = 0
        self.identifier_re = compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
        self.terminal_re = compile(r'"[^"]*"')
        self.operators = {'=', ',', '|', '{', '}', '[', ']', '(', ')', ';'}

    def tokenise(self):
        while self.pointer < len(self.ebnf_str):

            char = self.ebnf_str[self.pointer]

            if char.isspace():
                self.pointer += 1
                continue

            if char in self.operators:
                self.token_stream.append(Token("OPERATOR", char))
                self.pointer += 1
                continue

            terminal_match = self.terminal_re.match(self.ebnf_str, self.pointer)
            if terminal_match:
                self.token_stream.append(Token("TERMINAL", terminal_match.group(0)[1:-1]))
                self.pointer = terminal_match.end()
                continue

            identifier_match = self.identifier_re.match(self.ebnf_str, self.pointer)
            if identifier_match:
                self.token_stream.append(Token("IDENTIFIER", identifier_match.group(0)))
                self.pointer = identifier_match.end()
                continue

        return self.token_stream


class Parser:
    def __init__(self, token_stream):
        self.tokens = token_stream
        self.pointer = 0

    def look(self):
        if self.pointer < len(self.tokens):
            return self.tokens[self.pointer]
        return None

    def eat(self, expect_t, expect_v=None):
        token = self.look()

        if not token:
            raise SyntaxError("You can't end the token stream here idiot")

        if token.type != expect_t:
            raise SyntaxError(f"Expected {expect_t}, got {token.type}")

        if expect_v and token.value != expect_v:
            raise SyntaxError(f"Expected {expect_v}, got {token.value}")

        self.pointer += 1
        return token

    def parse_grammar(self):
        rules = []

        while self.look():
            rules.append(self.parse_rule())

        return GrammarNode(rules)

    def parse_rule(self):
        left = self.eat("IDENTIFIER")
        self.eat("OPERATOR", "=")

        right = self.parse_expression()
        self.eat("OPERATOR", ";")

        return RuleNode(left.value, right)

    def parse_expression(self):
        nodes = [self.parse_concatenation()]

        while self.look() and self.look().type == "OPERATOR" and self.look().value == "|":
            self.eat("OPERATOR", "|")
            nodes.append(self.parse_concatenation())

        if len(nodes) == 1:
            return nodes[0]
        return OrNode(nodes)

    def parse_concatenation(self):
        nodes = [self.parse_term()]

        while self.look() and self.look().type == "OPERATOR" and self.look().value == ",":
            self.eat("OPERATOR", ",")
            nodes.append(self.parse_term())

        if len(nodes) == 1:
            return nodes[0]
        return ConcatenationNode(nodes)

    def parse_term(self):
        token = self.look()

        if token.type == "IDENTIFIER":
            self.eat("IDENTIFIER")
            return IdentifierNode(token.value)

        if token.type == "TERMINAL":
            self.eat("TERMINAL")
            if token.value:
                return TerminalNode(token.value)
            return EpsilonNode()

        if token.type == "OPERATOR" and token.value == "{":
            self.eat("OPERATOR", "{")
            inner = self.parse_expression()
            self.eat("OPERATOR", "}")
            return RepeatNode(inner)

        if token.type == "OPERATOR" and token.value == "[":
            self.eat("OPERATOR", "[")
            inner = self.parse_expression()
            self.eat("OPERATOR", "]")
            return OptionalNode(inner)

        if token.type == "OPERATOR" and token.value == "(":
            self.eat("OPERATOR", "(")
            inner = self.parse_expression()
            self.eat("OPERATOR", ")")
            return GroupingNode(inner)


class Flattener:
    def __init__(self, start_node):
        self.start_node = start_node
        self.flattened_rules = []
        self.autogen_counter = 1

    def get_autogen_name(self):
        name = f"autogen_{self.autogen_counter}"
        self.autogen_counter += 1
        return name

    def flatten_grammar(self):
        for rule in self.start_node.children:
            right = self.walk(rule.right, is_top_level=True)
            self.flattened_rules.append(RuleNode(rule.left, right))

        return GrammarNode(self.flattened_rules)

    def walk(self, node, is_top_level=False):
        if isinstance(node, (IdentifierNode, TerminalNode, EpsilonNode)):
            return node

        if isinstance(node, ConcatenationNode):
            return ConcatenationNode([self.walk(child) for child in node.children])

        if isinstance(node, OrNode):
            node = OrNode([self.walk(child) for child in node.children])
            if is_top_level:
                return node
            name = self.get_autogen_name()
            self.flattened_rules.append(RuleNode(name, node))
            return IdentifierNode(name)

        if isinstance(node, RepeatNode):
            name = self.get_autogen_name()
            inner = self.walk(node.inner)

            # <autogen> -> inner, <autogen>
            recursive_rule = ConcatenationNode([inner, IdentifierNode(name)])
            # <autogen> -> epsilon
            terminating_rule = OrNode([recursive_rule, EpsilonNode()])

            self.flattened_rules.append(RuleNode(name, terminating_rule))
            return IdentifierNode(name)

        if isinstance(node, OptionalNode):
            name = self.get_autogen_name()
            inner = self.walk(node.inner)

            # <autogen> -> inner | epsilon
            rule = OrNode([inner, EpsilonNode()])
            self.flattened_rules.append(RuleNode(name, rule))
            return IdentifierNode(name)

        if isinstance(node, GroupingNode):
            return self.walk(node.inner)


class FirstSet:
    def __init__(self, start_node):
        self.rules = {rule.left: rule.right for rule in start_node.children}
        self.first_sets = {name: set() for name in self.rules.keys()}
        self.epsilon = "ε"

    def calculate(self):
        changed = True

        while changed:
            changed = False
            for name, node in self.rules.items():
                start_cnt = len(self.first_sets[name])
                node_first_set = self.get_first(node)
                self.first_sets[name].update(node_first_set)
                if len(self.first_sets[name]) > start_cnt:
                    changed = True

        return self.first_sets

    def get_first(self, node):
        if isinstance(node, TerminalNode):
            return {node.value}

        if isinstance(node, EpsilonNode):
            return {self.epsilon}

        if isinstance(node, IdentifierNode):
            return set(self.first_sets[node.value])

        if isinstance(node, OrNode):
            result = set()
            for child in node.children:
                result.update(self.get_first(child))
            return result

        if isinstance(node, ConcatenationNode):
            result = set()
            for child in node.children:
                child_first_set = self.get_first(child)
                result.update(child_first_set - {self.epsilon})
                if self.epsilon not in child_first_set:
                    break
            else:
                result.add(self.epsilon)
            return result

        return set()


class FollowSet:
    def __init__(self, start_node, first_calc, start_rule_name):
        self.rules = {rule.left: rule.right for rule in start_node.children}
        self.first_calc = first_calc
        self.follow_sets = {name: set() for name in self.rules.keys()}
        self.epsilon = "ε"
        self.follow_sets[start_rule_name].add("⊣")

    def calculate(self):
        changed = True

        while changed:
            changed = False
            for name, node in self.rules.items():
                if self.get_follow(name, node):
                    changed = True

        return self.follow_sets

    def get_follow(self, parent, node):
        changed = False

        if isinstance(node, OrNode):
            for child in node.children:

                if isinstance(child, IdentifierNode):
                    target = child.value
                    start_cnt = len(self.follow_sets[target])
                    self.follow_sets[target].update(self.follow_sets[parent])
                    if len(self.follow_sets[target]) > start_cnt:
                        changed = True

                if self.get_follow(parent, child):
                    changed = True

        if isinstance(node, ConcatenationNode):
            for i in range(len(node.children)):
                child = node.children[i]

                if isinstance(child, IdentifierNode):
                    target = child.value
                    start_cnt = len(self.follow_sets[target])
                    following_nodes = node.children[i+1:]

                    if following_nodes:
                        following_first = self.get_seq_first(following_nodes)
                        self.follow_sets[target].update(following_first - {self.epsilon})

                        if self.epsilon in following_first:
                            self.follow_sets[target].update(self.follow_sets[parent])

                    else:
                        self.follow_sets[target].update(self.follow_sets[parent])

                    if len(self.follow_sets[target]) > start_cnt:
                        changed = True

                if self.get_follow(parent, child):
                    changed = True

        return changed

    def get_seq_first(self, seq):
        result = set()
        for node in seq:
            child_first = self.first_calc.get_first(node)
            result.update(child_first - {self.epsilon})

            if self.epsilon not in child_first:
                break
        else:
            result.add(self.epsilon)
        return result


class ParseTable:
    def __init__(self, start_node, first_calc, follow_sets):
        self.rules = {rule.left: rule.right for rule in start_node.children}
        self.first_calc = first_calc
        self.follow_sets = follow_sets
        self.table = {name: {} for name in self.rules.keys()}
        self.epsilon = "ε"

    def generate(self):
        for name, node in self.rules.items():
            if isinstance(node, OrNode):
                choices = node.children
            else:
                choices = [node]

            for choice in choices:
                choice_first = self.first_calc.get_first(choice)

                for terminal in choice_first - {self.epsilon}:
                    self.add_to_table(name, terminal, choice)

                if self.epsilon in choice_first:
                    for terminal in self.follow_sets[name]:
                        self.add_to_table(name, terminal, choice)

        return self.table

    def add_to_table(self, non_terminal, terminal, choice):
        if terminal in self.table[non_terminal]:
            current_choice = self.table[non_terminal][terminal]
            if current_choice != choice:
                raise AssertionError("Language is not LL(1)")

        self.table[non_terminal][terminal] = choice

    def print_table(self):
        for non_term, row in self.table.items():
            print(f"{non_term}:")
            for term, choice in row.items():
                print(f"  {term} -> {choice}")


class LL1Parser:
    def __init__(self, parse_table, debug=False):
        self.parse_table = parse_table
        self.debug = debug
        if self.debug:
            with open("log.txt", "w", encoding="utf-8"):
                pass

    def parse(self, input_str, start_rule_name):
        tokens = input_str + ["⊣"]
        pointer = 0
        stack = ["⊣", start_rule_name]

        self.debug_print(f"Beginning parsing of '{input_str}'")

        while len(stack) > 0:
            top = stack.pop()
            current = tokens[pointer]

            self.debug_print(f"Token: '{current}' | Top: '{top}'")

            if top == current:
                self.debug_print(f"MATCHED '{current}'")
                pointer += 1

            elif top in self.parse_table:
                if current not in self.parse_table[top]:
                    self.debug_print(f"Unexpected token '{current}' while parsing '{top}' -- EXITING")
                    return False

                choice = self.parse_table[top][current]
                self.debug_print(f"EXPANDING {top} to {choice}")
                symbols = self.extract_symbols(choice)

                for symbol in reversed(symbols):
                    if symbol != "ε":
                        stack.append(symbol)

            else:
                self.debug_print(f"Expected '{top}', but found '{current}' -- EXITING")
                return False

        self.debug_print("Parse Successful -- EXITING")
        return True

    def extract_symbols(self, node):
        if isinstance(node, EpsilonNode):
            return ["ε"]
        if isinstance(node, (TerminalNode, IdentifierNode)):
            return [node.value]
        if isinstance(node, ConcatenationNode):
            symbols = []
            for child in node.children:
                symbols.extend(self.extract_symbols(child))
            return symbols

    def debug_print(self, msg):
        if not self.debug:
            return
        with open("log.txt", "a", encoding='utf-8') as f:
            f.write(f"[ DEBUG ] {msg}\n")


class Engine:
    def __init__(self, start_rule_name, rule_file="rules.txt"):
        self.start_rule_name = start_rule_name
        self.rule_file = rule_file

        with open(self.rule_file, "r", encoding="utf-8") as f:
            self.ebnf = f.read()

        self.lexer = Lexer(self.ebnf)
        self.token_stream = self.lexer.tokenise()
        print("Token Stream Generated")

        self.parser = Parser(self.token_stream)
        self.ast = self.parser.parse_grammar()
        print("AST Generated")

        self.flattener = Flattener(self.ast)
        self.flat_ast = self.flattener.flatten_grammar()
        print("AST Flattened")

        self.first_calc = FirstSet(self.flat_ast)
        self.first_sets = self.first_calc.calculate()
        print("First Sets Generated")

        self.follow_calc = FollowSet(self.flat_ast, self.first_calc, self.start_rule_name)
        self.follow_sets = self.follow_calc.calculate()
        print("Follow Sets Generated")

        self.table_gen = ParseTable(self.flat_ast, self.first_calc, self.follow_sets)
        self.ll1_table = self.table_gen.generate()
        print("Generated LL(1) Parse Table")

    def parse(self, input_stream, debug=False):
        ll1_parser = LL1Parser(self.ll1_table, debug=debug)
        return ll1_parser.parse(input_stream, self.start_rule_name)
