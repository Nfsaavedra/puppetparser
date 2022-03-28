class CodeElement:
    def __init__(self, line: int, col: int) -> None:
        self.line: int = line
        self.col: int = col

class Attribute(CodeElement):
    def __init__(self, line: int, col: int, key: str, value) -> None:
        super().__init__(line, col)
        self.key = key
        self.value = value

class Resource(CodeElement):
    def __init__(self, line: int, col: int, type: str, title: str, attributes: list[Attribute]) -> None:
        super().__init__(line, col)
        self.type = type
        self.title = title
        self.attributes = attributes