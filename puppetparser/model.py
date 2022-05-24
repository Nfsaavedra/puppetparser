from typing import Union

class CodeElement:
    def __init__(self, line: int, col: int, end_line: int, end_col: int) -> None:
        self.line: int = line
        self.col: int = col
        self.end_line: int = end_line
        self.end_col: int = end_col

class Value(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, value) -> None:
        super().__init__(line, col, end_line, end_col)
        self.value = value

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, Value) and __o.value == self.value

    def __hash__(self) -> int:
        return self.value.__hash__()

class Hash(Value):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, value: dict) -> None:
        super().__init__(line, col, end_line, end_col, value)

class Array(Value):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, value: list) -> None:
        super().__init__(line, col, end_line, end_col, value)

class Regex(Value):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, value: str):
        super().__init__(line, col, end_line, end_col, value)

class Attribute(CodeElement):
    def __init__(self, key: Value, value: Value) -> None:
        super().__init__(key.line, key.col, value.end_line, value.end_col)
        self.key: Value = key
        self.value: Value = value

class Resource(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, 
            type: Union[str, 'Reference', 'ResourceCollector'], title: str, attributes: list[Attribute]) -> None:
        super().__init__(line, col, end_line, end_col)
        self.type = type
        self.title: str = title
        self.attributes: list[Attribute] = attributes

class ResourceDeclaration(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, 
            name: str, parameters: list, block: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.name = name
        self.parameters = parameters
        self.block = block

class Parameter(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, 
            type: str, name: str, default) -> None:
        super().__init__(line, col, end_line, end_col)
        self.type: str = type
        self.name: str = name
        self.default = default

class Assignment(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, name, value) -> None:
        super().__init__(line, col, end_line, end_col)
        self.name = name
        self.value = value

class PuppetClass(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, name: str, 
            block: list, inherits: str, parameters: Union[list[Parameter], list[Attribute]]) -> None:
        super().__init__(line, col, end_line, end_col)
        self.name: str = name
        self.block: list = block
        self.inherits: str = inherits
        self.parameters: Union[list[Parameter], list[Attribute]] = parameters

class ClassAsResource(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, 
            title: str, attributes: list[Attribute]) -> None:
        super().__init__(line, col, end_line, end_col)
        self.title: str = title
        self.attributes: list[Attribute] = attributes
    
class Node(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int,
            name: str, block: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.name: str = name
        self.block: list = block

class Comment(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, content: str):
        super().__init__(line, col, end_line, end_col)
        self.content = content

class Operation(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int,
            arguments: tuple, operator: str):
        super().__init__(line, col, end_line, end_col)
        self.arguments: tuple = arguments
        self.operator: str = operator

class Lambda(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, 
            parameters: tuple, block: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.parameters = parameters
        self.block = block

class FunctionCall(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, name: str, arguments: tuple, lamb: Lambda) -> None:
        super().__init__(line, col, end_line, end_col)
        self.name = name
        self.arguments = arguments
        self.lamb = lamb

class If(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, condition: CodeElement, block: list, 
            elseblock: 'If') -> None:
        super().__init__(line, col, end_line, end_col)
        self.condition = condition
        self.block = block
        self.elseblock = elseblock

class Unless(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, condition: CodeElement, block: list, 
            elseblock: 'Unless') -> None:
        super().__init__(line, col, end_line, end_col)
        self.condition = condition
        self.block = block
        self.elseblock = elseblock

class Include(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, inc: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.inc = inc

class Import(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, imp: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.imp = imp

class Require(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, req: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.req = req

class Contain(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, cont: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.cont = cont

class Debug(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, args: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.args = args

class Fail(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, args: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.args = args

class Realize(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, classes: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.classes = classes

class Tag(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, tags: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.tags = tags

class Match(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, 
            expressions: list, block: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.expressions = expressions
        self.block = block

class Case(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int,
            control: CodeElement, matches: list[Match]) -> None:
        super().__init__(line, col, end_line, end_col)
        self.control = control
        self.matches = matches

class Selector(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int,
            control: CodeElement, hash: dict) -> None:
        super().__init__(line, col, end_line, end_col)
        self.control = control
        self.hash = hash

class Reference(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, 
            type: str, references: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.type: str = type
        self.references: list = references

class Function(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int,
            name: str, parameters: list, return_type, body: list) -> None:
        super().__init__(line, col, end_line, end_col)
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

class ResourceCollector(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, resource_type: str, search) -> None:
        super().__init__(line, col, end_line, end_col)
        self.resource_type = resource_type
        self.search = search

class ResourceExpression(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, 
            default: Resource, resources: list[Resource]) -> None:
        super().__init__(line, col, end_line, end_col)
        self.default = default
        self.resources = resources

class Chaining(CodeElement):
    def __init__(self, op1: CodeElement, op2: CodeElement, direction: str) -> None:
        super().__init__(op1.line, op1.col, op2.end_line, op2.end_col)
        self.op1 = op1
        self.op2 = op2
        self.direction = direction