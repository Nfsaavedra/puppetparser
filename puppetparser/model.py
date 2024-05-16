from types import NoneType
from typing import Dict, List, Tuple, Optional, Generic, TypeVar

T = TypeVar(
    "T",
    str,
    int,
    float,
    bool,
    NoneType,
    Dict["CodeElement", "CodeElement"],
    List["CodeElement"],
)


class CodeElement:
    def __init__(self, line: int, col: int, end_line: int, end_col: int) -> None:
        self.line: int = line
        self.col: int = col
        self.end_line: int = end_line
        self.end_col: int = end_col

    def __hash__(self) -> int:
        return hash((self.line, self.col, self.end_line, self.end_col))


class Value(CodeElement, Generic[T]):
    def __init__(
        self, line: int, col: int, end_line: int, end_col: int, value: T
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.value: T = value

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.__class__):
            return False
        return self.value == __o.value

    def __hash__(self) -> int:
        if self.value is None:
            return 0

        return self.value.__hash__()  # type: ignore


class Hash(Value[Dict[CodeElement, CodeElement]]):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        value: Dict[CodeElement, CodeElement],
    ) -> None:
        super().__init__(line, col, end_line, end_col, value)


class Array(Value[List[CodeElement]]):
    def __init__(
        self, line: int, col: int, end_line: int, end_col: int, value: List[CodeElement]
    ) -> None:
        super().__init__(line, col, end_line, end_col, value)


class Regex(Value[str]):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, value: str):
        super().__init__(line, col, end_line, end_col, value)


class Attribute(CodeElement):
    def __init__(self, key: CodeElement, value: CodeElement) -> None:
        super().__init__(key.line, key.col, value.end_line, value.end_col)
        self.key: CodeElement = key
        self.value: CodeElement = value


class Resource(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        type: Value[str],
        title: Value[str] | None,
        attributes: List[Attribute],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.type = type
        self.title: Value[str] | None = title
        self.attributes: list[Attribute] = attributes


class ResourceDeclaration(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        name: str,
        parameters: List["Parameter"],
        block: List[CodeElement],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.name = name
        self.parameters = parameters
        self.block = block


class Parameter(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        type: str | CodeElement,
        name: str,
        default: CodeElement | None,
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.type: str | CodeElement = type
        self.name: str = name
        self.default = default


class Assignment(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        name: CodeElement,
        value: CodeElement,
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.name = name
        self.value = value


class PuppetClass(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        name: str,
        block: List[CodeElement],
        inherits: str,
        parameters: List[Parameter] | List[Attribute],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.name: str = name
        self.block: List[CodeElement] = block
        self.inherits: str = inherits
        self.parameters: List[Parameter] | List[Attribute] = parameters


class ClassAsResource(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        title: str,
        attributes: List[Attribute],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.title: str = title
        self.attributes: List[Attribute] = attributes


class Node(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        name: str,
        block: List[CodeElement],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.name: str = name
        self.block: List[CodeElement] = block


class Comment(CodeElement):
    def __init__(self, line: int, col: int, end_line: int, end_col: int, content: str):
        super().__init__(line, col, end_line, end_col)
        self.content = content


class Operation(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        arguments: Tuple[CodeElement, ...],
        operator: str,
    ):
        super().__init__(line, col, end_line, end_col)
        self.arguments: List[CodeElement] = list(arguments)
        self.operator: str = operator


class Lambda(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        parameters: Tuple[CodeElement, ...],
        block: List[CodeElement],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.parameters = parameters
        self.block = block


class FunctionCall(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        name: Value[str],
        arguments: List[CodeElement],
        lamb: Lambda | None,
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.name = name
        self.arguments = arguments
        self.lamb = lamb


class If(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        condition: CodeElement | None,
        block: List[CodeElement],
        elseblock: Optional["If"],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.condition = condition
        self.block = block
        self.elseblock = elseblock


class Unless(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        condition: CodeElement | None,
        block: List[CodeElement],
        elseblock: Optional["Unless"],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.condition = condition
        self.block = block
        self.elseblock = elseblock


class Include(CodeElement):
    def __init__(
        self, line: int, col: int, end_line: int, end_col: int, inc: List[CodeElement]
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.inc = inc


class Import(CodeElement):
    def __init__(
        self, line: int, col: int, end_line: int, end_col: int, imp: List[CodeElement]
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.imp = imp


class Require(CodeElement):
    def __init__(
        self, line: int, col: int, end_line: int, end_col: int, req: List[CodeElement]
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.req = req


class Contain(CodeElement):
    def __init__(
        self, line: int, col: int, end_line: int, end_col: int, cont: List[CodeElement]
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.cont = cont


class Debug(CodeElement):
    def __init__(
        self, line: int, col: int, end_line: int, end_col: int, args: List[CodeElement]
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.args = args


class Fail(CodeElement):
    def __init__(
        self, line: int, col: int, end_line: int, end_col: int, args: List[CodeElement]
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.args = args


class Realize(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        classes: List[CodeElement],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.classes = classes


class Tag(CodeElement):
    def __init__(
        self, line: int, col: int, end_line: int, end_col: int, tags: List[CodeElement]
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.tags = tags


class Match(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        expressions: List[CodeElement],
        block: List[CodeElement],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.expressions = expressions
        self.block = block


class Case(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        control: CodeElement,
        matches: List[Match],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.control = control
        self.matches = matches


class Selector(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        control: CodeElement,
        hash: Hash,
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.control = control
        self.hash = hash


class Reference(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        type: str,
        references: List[CodeElement],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.type: str = type
        self.references: List[CodeElement] = references


class Function(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        name: str,
        parameters: List[Parameter],
        return_type: Value[str] | None,
        body: List[CodeElement],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body


class ResourceCollector(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        resource_type: str,
        search: CodeElement | None,
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.resource_type = resource_type
        self.search = search


class ResourceExpression(CodeElement):
    def __init__(
        self,
        line: int,
        col: int,
        end_line: int,
        end_col: int,
        default: Resource | None,
        resources: List[Resource],
    ) -> None:
        super().__init__(line, col, end_line, end_col)
        self.default = default
        self.resources = resources


class Chaining(CodeElement):
    def __init__(self, op1: CodeElement, op2: CodeElement, direction: str) -> None:
        super().__init__(op1.line, op1.col, op2.end_line, op2.end_col)
        self.op1 = op1
        self.op2 = op2
        self.direction = direction
