from re import compile


class Token:
    def __init__(self, _type, _value):
        self.type = _type
        self.value = _value


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
        self.operators = {'=', ',', '|', '{', '}', '[', ']', ';'}

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
                self.token_stream.append(Token("TERMINAL", terminal_match.group(0)))
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
            return TerminalNode(token.value)

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
            right = self.walk(rule.right)
            self.flattened_rules.append(RuleNode(rule.left, right))

        return GrammarNode(self.flattened_rules)

    def walk(self, node):
        if isinstance(node, (IdentifierNode, TerminalNode, EpsilonNode)):
            return node

        if isinstance(node, ConcatenationNode):
            return ConcatenationNode([self.walk(child) for child in node.children])

        if isinstance(node, OrNode):
            return OrNode([self.walk(child) for child in node.children])

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
                if self.find_follow(name, node):
                    changed = True

        return self.follow_sets

    def find_follow(self, parent, node):
        changed = False

        if isinstance(node, OrNode):
            for child in node.children:

                if isinstance(child, IdentifierNode):
                    target = child.value
                    start_cnt = len(self.follow_sets[target])
                    self.follow_sets[target].update(self.follow_sets[parent])
                    if len(self.follow_sets[target]) > start_cnt:
                        changed = True

                if self.find_follow(parent, child):
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

                if self.find_follow(parent, child):
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
