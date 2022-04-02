from typing import Union

class CodeElement:
    def __init__(self, line: int, col: int) -> None:
        self.line: int = line
        self.col: int = col

class Attribute(CodeElement):
    def __init__(self, line: int, col: int, key: str, value) -> None:
        super().__init__(line, col)
        self.key: str = key
        self.value: str = value

class Resource(CodeElement):
    def __init__(self, line: int, col: int, type: Union[str, 'Reference'], title: str, attributes: list[Attribute]) -> None:
        super().__init__(line, col)
        self.type = type
        self.title: str = title
        self.attributes: list[Attribute] = attributes

class ResourceDeclaration(CodeElement):
    def __init__(self, line: int, col: int, name: str, parameters: list, block: list) -> None:
        super().__init__(line, col)
        self.name = name
        self.parameters = parameters
        self.block = block

class Parameter(CodeElement):
    def __init__(self, line: int, col: int, type: str, name: str, default) -> None:
        super().__init__(line, col)
        self.type: str = type
        self.name: str = name
        self.default = default

class Assignment(CodeElement):
    def __init__(self, line: int, col: int, name, value) -> None:
        super().__init__(line, col)
        self.name = name
        self.value = value

class PuppetClass(CodeElement):
    def __init__(self, line: int, col: int, name: str, 
            block: list, inherits: str, parameters: list[Parameter]) -> None:
        super().__init__(line, col)
        self.name: str = name
        self.block: list = block
        self.inherits: str = inherits
        self.parameters: list[Parameter] = parameters
    
class Node(CodeElement):
    def __init__(self, line: int, col: int, name: str, block: list) -> None:
        super().__init__(line, col)
        self.name: str = name
        self.block: list = block

class Comment(CodeElement):
    def __init__(self, line: int, col: int, content: str):
        super().__init__(line, col)
        self.content = content

class Regex:
    def __init__(self, content: str):
        self.content = content

#FIXME probably should be a codeelement
class Operation:
    def __init__(self, arguments: tuple, operator: str):
        self.arguments: tuple = arguments
        self.operator: str = operator

class Lambda(CodeElement):
    def __init__(self, line: int, col: int, parameters: tuple, block: list) -> None:
        super().__init__(line, col)
        self.parameters = parameters
        self.block = block

class FunctionCall(CodeElement):
    def __init__(self, line: int, col: int, name: str, arguments: tuple, lamb: Lambda) -> None:
        super().__init__(line, col)
        self.name = name
        self.arguments = arguments
        self.lamb = lamb

class If(CodeElement):
    def __init__(self, line: int, col: int, condition: CodeElement, block: list, 
            elseblock: 'If') -> None:
        super().__init__(line, col)
        self.condition = condition
        self.block = block
        self.elseblock = elseblock

class Unless(CodeElement):
    def __init__(self, line: int, col: int, condition: CodeElement, block: list, 
            elseblock: 'Unless') -> None:
        super().__init__(line, col)
        self.condition = condition
        self.block = block
        self.elseblock = elseblock

class Include(CodeElement):
    def __init__(self, line: int, col: int, inc: list) -> None:
        super().__init__(line, col)
        self.inc = inc

class Require(CodeElement):
    def __init__(self, line: int, col: int, req: list) -> None:
        super().__init__(line, col)
        self.req = req

class Contain(CodeElement):
    def __init__(self, line: int, col: int, cont: list) -> None:
        super().__init__(line, col)
        self.cont = cont

class Debug(CodeElement):
    def __init__(self, line: int, col: int, args: list) -> None:
        super().__init__(line, col)
        self.args = args

class Fail(CodeElement):
    def __init__(self, line: int, col: int, args: list) -> None:
        super().__init__(line, col)
        self.args = args

class Tag(CodeElement):
    def __init__(self, line: int, col: int, tags: list) -> None:
        super().__init__(line, col)
        self.tags = tags

class Match(CodeElement):
    def __init__(self, line: int, col: int, expressions: list, block: list) -> None:
        super().__init__(line, col)
        self.expressions = expressions
        self.block = block

class Case(CodeElement):
    def __init__(self, line: int, col: int, control: CodeElement, matches: list[Match]) -> None:
        super().__init__(line, col)
        self.control = control
        self.matches = matches

class Selector(CodeElement):
    def __init__(self, line: int, col: int, control: CodeElement, hash: dict) -> None:
        super().__init__(line, col)
        self.control = control
        self.hash = hash

class Reference(CodeElement):
    def __init__(self, line: int, col: int, type: str, references: list) -> None:
        super().__init__(line, col)
        self.type: str = type
        self.references: list = references

class Function(CodeElement):
    def __init__(self, line: int, col: int, name: str, parameters: list, 
            return_type, body: list) -> None:
        super().__init__(line, col)
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body