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
    def __init__(self, line: int, col: int, type: str, title: str, attributes: list[Attribute]) -> None:
        super().__init__(line, col)
        self.type: str = type
        self.title: str = title
        self.attributes: list[Attribute] = attributes

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
