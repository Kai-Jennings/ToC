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

        token = self.look()
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
