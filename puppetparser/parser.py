# pyright: reportUnusedFunction=false, reportUnusedVariable=false
from ply.lex import lex, LexToken
from ply.yacc import yacc, YaccProduction
import tempfile
import re, os
from typing import Tuple, List
from puppetparser.model import *
from puppetparser import parser as pf


class InvalidPuppetScript(Exception):
    pass


def find_column(input: str, pos: int) -> int:
    rfind = input.rfind("\n", 0, pos)
    if rfind == -1:
        return pos + 1
    line_start = rfind + 1
    return (pos - line_start) + 1


def parse(script: str) -> Tuple[List[CodeElement], List[Comment]]:
    comments: List[Comment] = []

    tokens = (
        # Keywords
        "APPLICATION",
        "ATTR",
        "CASE",
        "COMPONENT",
        "CONSUMES",
        "DEFAULT",
        "DEFINE",
        "ELSIF",
        "ELSE",
        "FALSE",
        "FUNCTION",
        "IF",
        "IMPORT",
        "IN",
        "INHERITS",
        "NODE",
        "PRODUCES",
        "REGEXP",
        "SITE",
        "TRUE",
        "TYPE",
        "UNDEF",
        "UNLESS",
        # Values
        "STRING",
        "INTEGER",
        "FLOAT",
        "REGEXPRESSION",
        # SUGAR SYNTAX
        "LBRACKET",
        "RBRACKET",
        "LANGLEBRACKET",
        "RANGLEBRACKET",
        "LPAREN",
        "RPAREN",
        "LPARENR",
        "RPARENR",
        "EQUAL",
        "COLON",
        "HASH_ROCKET",
        "COMMA",
        "BAR",
        "DOT",
        "QUESTION_MARK",
        "AT",
        "DOT_COMMA",
        "PLUSIGNMENT",
        # Identifiers
        "ID",
        "ID_TYPE",
        "SENSITIVE",
        # Special
        "CLASS",
        # Comparison operators
        "CMP_EQUAL",
        "CMP_NOT_EQUAL",
        "CMP_LESS_THAN",
        "CMP_GREATER_THAN",
        "CMP_LESS_THAN_OR_EQUAL",
        "CMP_GREATER_THAN_OR_EQUAL",
        "CMP_REGEX_MATCH",
        "CMP_REGEX_NOT_MATCH",
        "CMP_IN",
        # Boolean operators
        "BOOL_AND",
        "BOOL_OR",
        "BOOL_NOT",
        # Arithmetic operators
        "ARITH_ADD",
        "ARITH_SUB",
        "ARITH_DIV",
        "ARITH_MUL",
        "ARITH_MOD",
        "ARITH_LSHIFT",
        "ARITH_RSHIFT",
        # Statement functions
        "INCLUDE",
        "REQUIRE",
        "CONTAIN",
        "TAG",
        "DEBUG",
        "INFO",
        "NOTICE",
        "WARNING",
        "ERR",
        "FAIL",
        "REALIZE",
        # Chaining arrows
        "CHAINING_LEFT",
        "CHAINING_RIGHT",
    )

    statement_functions = {
        "include": "INCLUDE",
        "require": "REQUIRE",
        "contain": "CONTAIN",
        "tag": "TAG",
        "debug": "DEBUG",
        "info": "INFO",
        "notice": "NOTICE",
        "warning": "WARNING",
        "err": "ERR",
        "fail": "FAIL",
        "realize": "REALIZE",
        "import": "IMPORT",
    }

    statement_functions_class = {
        "include": "Include",
        "require": "Require",
        "contain": "Contain",
        "tag": "Tag",
        "debug": "Debug",
        "info": "Debug",
        "notice": "Debug",
        "warning": "Debug",
        "err": "Debug",
        "fail": "Fail",
        "realize": "Realize",
        "import": "Import",
    }

    keywords = {
        "and": "BOOL_AND",
        "application": "APPLICATION",
        "attr": "ATTR",
        "case": "CASE",
        "component": "COMPONENT",
        "consumes": "CONSUMES",
        "default": "DEFAULT",
        "define": "DEFINE",
        "elsif": "ELSIF",
        "else": "ELSE",
        "false": "FALSE",
        "function": "FUNCTION",
        "if": "IF",
        "import": "IMPORT",
        "in": "CMP_IN",
        "inherits": "INHERITS",
        "node": "NODE",
        "or": "BOOL_OR",
        "produces": "PRODUCES",
        "regexp": "REGEXP",
        "site": "SITE",
        "true": "TRUE",
        "type": "TYPE",
        "undef": "UNDEF",
        "unless": "UNLESS",
        "class": "CLASS",
    }

    states = (("comment", "exclusive"), ("regex", "exclusive"), ("docs", "exclusive"))

    # Other
    t_LBRACKET = r"\{"
    t_RBRACKET = r"\}"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LPARENR = r"\["
    t_RPARENR = r"\]"
    t_QUESTION_MARK = r"\?"
    t_BAR = r"\|"
    t_AT = r"@"
    t_HASH_ROCKET = r"=>"
    t_PLUSIGNMENT = r"\+>"
    t_COLON = r"\:"
    t_COMMA = r","
    t_DOT_COMMA = r";"
    t_DOT = r"\."
    t_CMP_EQUAL = r"=="
    t_CMP_NOT_EQUAL = r"!="
    t_CMP_LESS_THAN = r"<"
    t_CMP_GREATER_THAN = r">"
    t_CMP_LESS_THAN_OR_EQUAL = r"<="
    t_CMP_GREATER_THAN_OR_EQUAL = r">="
    t_CMP_REGEX_MATCH = r"=~"
    t_CMP_REGEX_NOT_MATCH = r"!~"
    t_EQUAL = r"\="
    t_BOOL_NOT = r"!"
    t_ARITH_ADD = r"\+"
    t_ARITH_SUB = r"-"
    t_ARITH_DIV = r"\/"
    t_ARITH_MUL = r"\*"
    t_ARITH_MOD = r"%"
    t_ARITH_LSHIFT = r"<<"
    t_ARITH_RSHIFT = r">>"
    t_CHAINING_RIGHT = r"->|~>"
    t_CHAINING_LEFT = r"<-|<~"
    t_LANGLEBRACKET = r"(\<\<\|)|(\<\|)"
    t_RANGLEBRACKET = r"(\|\>\>)|(\|\>)"

    # Identifiers
    t_ignore_ANY = r"[\t\ ]"

    def t_newline(t: LexToken):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_COMMENT(t: LexToken):
        r"\#.*(\n?)"
        column = find_column(script, t.lexpos)
        value = t.value[1:-1]
        comments.append(
            Comment(t.lexer.lineno, column, t.lexer.lineno, column + len(value), value)
        )
        t.lexer.lineno += 1

    current_comment = Comment(0, 0, 0, 0, "")

    def t_comment(t: LexToken):
        r"\/\*"
        nonlocal current_comment
        current_comment = Comment(0, 0, 0, 0, "")
        current_comment.line = t.lexer.lineno
        current_comment.col = find_column(script, t.lexpos)
        t.lexer.begin("comment")

    def t_comment_END(t: LexToken):
        r"\*\/"
        new_lines = current_comment.content.count("\n")
        current_comment.end_line = current_comment.line + new_lines
        current_comment.end_col = len(current_comment.content.split("\n")[-1])
        comments.append(current_comment)
        t.lexer.begin("INITIAL")

    def t_comment_content(t: LexToken):
        r".|\n"
        current_comment.content += t.value
        t.lexer.lineno += t.value.count("\n")

    def t_regex_END(t: LexToken):
        r"\/"
        t.type = "ARITH_DIV"
        t.lexer.begin("INITIAL")
        return t

    def t_regex_expression(t: LexToken):
        r"((\\.)|[^\/])+"
        t.type = "REGEXPRESSION"
        return t

    def t_docs_END(t: LexToken):
        r"\|"
        t.type = "BAR"
        t.lexer.begin("INITIAL")
        return t

    def t_docs_string(t: LexToken):
        r"(\n|[^\|])+"
        t.lexer.lineno += t.value.count("\n")
        t.type = "STRING"
        return t

    def t_octal_INTEGER(t: LexToken):
        r"0[0-9]+"
        t.value = int(t.value, 8)  # type: ignore
        t.type = "INTEGER"
        return t

    def t_hexa_INTEGER(t: LexToken):
        r"0x[0-9a-f]+"
        t.value = int(t.value, 16)  # type: ignore
        t.type = "INTEGER"
        return t

    def t_NUMBER(t: LexToken):
        r"((0|[1-9]\d*)(\.\d+)?(e-?(0|[1-9]\d*))?)"
        if "." in t.value:
            t.type = "FLOAT"
        else:
            t.type = "INTEGER"
        return t

    def t_ID_TYPE(t: LexToken):
        r"((::)?[A-Za-z0-9\_\-]*(::))*[A-Z][a-zA-Z0-9\_\-]*"
        if t.value == "Sensitive":
            t.type = "SENSITIVE"
        return t

    def t_ID(t: LexToken):
        r"([a-z\$]|(::))((::)?[A-Za-z0-9\_\-]*)*"
        t.type = keywords.get(t.value, statement_functions.get(t.value, "ID"))
        return t

    def t_STRING(t: LexToken):
        r"(\'([^\\]|(\\(\n|.)))*?\')|(\"([^\\]|(\\(\n|.)))*?\")"
        t.value = t.value[1:-1]
        t.lexer.lineno += t.value.count("\n")
        return t

    def t_ANY_error(t: LexToken):
        raise InvalidPuppetScript(f"Lexer error {t}")

    lexer = lex()
    # Give the lexer some input
    lexer.input(script)

    # while True:
    #     tok = lexer.token()
    #     if not tok:
    #         break      # No more input
    #     print(tok)

    precedence = (
        ("nonassoc", "NO_LAMBDA"),
        ("nonassoc", "LAMBDA"),
        ("right", "CHAINING_RIGHT"),
        ("right", "CHAINING_LEFT"),
        ("left", "EQUAL"),
        ("left", "QUESTION_MARK"),
        ("left", "DOT"),
        ("left", "BOOL_OR"),
        ("left", "BOOL_AND"),
        (
            "nonassoc",
            "CMP_LESS_THAN",
            "CMP_GREATER_THAN",
            "CMP_LESS_THAN_OR_EQUAL",
            "CMP_GREATER_THAN_OR_EQUAL",
        ),
        ("nonassoc", "CMP_EQUAL", "CMP_NOT_EQUAL"),
        ("left", "ARITH_LSHIFT", "ARITH_RSHIFT"),
        ("left", "ARITH_ADD", "ARITH_SUB"),
        ("left", "ARITH_MUL", "ARITH_DIV", "ARITH_MOD"),
        ("left", "CMP_REGEX_MATCH", "CMP_REGEX_NOT_MATCH"),
        ("left", "CMP_IN"),
        ("right", "ARRAY_SPLAT"),
        ("right", "ARITH_MINUS"),
        ("right", "BOOL_NOT"),
        ("right", "LPARENR"),
        ("left", "LPAREN"),
        ("left", "BAR"),
    )

    start = "program"

    def p_program(p: YaccProduction):
        "program : block"
        p[0] = p[1]

    def p_class(p: YaccProduction):
        r"class : CLASS class_header LBRACKET block RBRACKET"
        p[0] = PuppetClass(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2][0],
            p[4],
            p[2][2],
            p[2][1],
        )

    def p_class_header(p: YaccProduction):
        r"class_header : ID LPAREN parameters RPAREN"
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            raise InvalidPuppetScript(f"Syntax error")
        p[0] = (p[1], p[3], "")

    def p_class_header_no_parameters(p: YaccProduction):
        r"class_header : ID"
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            raise InvalidPuppetScript(f"Syntax error")
        p[0] = (p[1], [], "")

    def p_class_header_pars_inherits(p: YaccProduction):
        r"class_header : ID LPAREN parameters RPAREN INHERITS ID"
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            raise InvalidPuppetScript(f"Syntax error")
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[6]):
            raise InvalidPuppetScript(f"Syntax error")
        p[0] = (p[1], p[3], p[6])

    def p_class_header_inherits(p: YaccProduction):
        r"class_header : ID INHERITS ID"
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            raise InvalidPuppetScript(f"Syntax error")
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[3]):
            raise InvalidPuppetScript(f"Syntax error")
        p[0] = (p[1], [], p[3])

    def p_class_resource_declaration(p: YaccProduction):
        r"class : CLASS LBRACKET resource_list RBRACKET"
        if len(p[3]) == 1:
            p[0] = ClassAsResource(
                p.lineno(1),
                find_column(script, p.lexpos(1)),
                p.lineno(4),
                find_column(script, p.lexpos(4)) + 1,
                p[3][0][0],
                p[3][0][1],
            )
        else:
            p[0] = list(
                map(lambda r: ClassAsResource(r[2], r[3], r[4], r[5], r[0], r[1]), p[3])
            )

    def p_node(p: YaccProduction):
        r"node : NODE STRING LBRACKET block RBRACKET"
        p[0] = Node(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2],
            p[4],
        )

    def p_node_id(p: YaccProduction):
        r"node : NODE ID LBRACKET block RBRACKET"
        p[0] = Node(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2],
            p[4],
        )

    def p_node_regex(p: YaccProduction):
        r"node : NODE regex LBRACKET block RBRACKET"
        p[0] = Node(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2],
            p[4],
        )

    def p_node_default(p: YaccProduction):
        r"node : NODE DEFAULT LBRACKET block RBRACKET"
        p[0] = Node(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2],
            p[4],
        )

    def p_assignment(p: YaccProduction):
        r"assignment : ID EQUAL expression"
        p[0] = Assignment(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p[3].end_line,
            p[3].end_col,
            p[1],
            p[3],
        )

    def p_assignment_access(p: YaccProduction):
        r"assignment : access EQUAL expression"
        p[0] = Assignment(p[1].line, p[1].col, p[3].end_line, p[3].end_col, p[1], p[3])

    def p_assignment_array(p: YaccProduction):
        r"assignment : array EQUAL array"
        if len(p[1].value) != len(p[3].value):
            raise InvalidPuppetScript(f"Syntax error")
        for id in p[1].value:
            if not re.match(r"^\$[a-z0-9_][a-zA-Z0-9_]*$", id.value) and not re.match(
                r"^\$([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*::[a-z0-9_][a-zA-Z0-9_]*$",
                id.value,
            ):
                raise InvalidPuppetScript(f"Syntax error")
        p[0] = Assignment(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p[3].end_line,
            p[3].end_col,
            p[1],
            p[3],
        )

    def p_assignment_hash(p: YaccProduction):
        r"assignment : array EQUAL hash"
        for id in p[1].value:
            if not re.match(r"^\$[a-z0-9_][a-zA-Z0-9_]*$", id.value) and not re.match(
                r"^\$([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*::[a-z0-9_][a-zA-Z0-9_]*$",
                id.value,
            ):
                raise InvalidPuppetScript(f"Syntax error")

            if id not in p[3].value:
                raise InvalidPuppetScript(f"Syntax error")

        p[0] = Assignment(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p[3].end_line,
            p[3].end_col,
            p[1],
            p[3],
        )

    def p_assignment_type_alias(p: YaccProduction):
        r"assignment : TYPE ID_TYPE EQUAL expression"
        p[0] = Assignment(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p[4].end_line,
            p[4].end_col,
            p[1] + " " + p[2],
            p[4],
        )

    def p_block(p: YaccProduction):
        r"block : statement block"
        p[0] = [p[1]] + p[2]

    def p_block_return(p: YaccProduction):
        r"block : expression"
        p[0] = [p[1]]

    def p_block_empty(p: YaccProduction):
        r"block : empty"
        p[0] = []

    def p_resource_id(p: YaccProduction):
        r"resource : ID LBRACKET resource_list RBRACKET"
        id = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            raise InvalidPuppetScript(f"Syntax error")
        if len(p[3]) == 1:
            p[0] = Resource(
                id.line,
                id.col,
                p.lineno(4),
                find_column(script, p.lexpos(4)) + 1,
                id,
                p[3][0][0],
                p[3][0][1],
            )
        else:
            resources = list(
                map(lambda r: Resource(r[2], r[3], r[4], r[5], id, r[0], r[1]), p[3])
            )
            default = None
            for r in resources:
                if isinstance(r.title, Value) and r.title.value == "default":
                    default = r
                    break
            resources = list(
                filter(
                    lambda r: isinstance(r.title, Value) and r.title.value != "default",
                    resources,
                )
            )

            p[0] = ResourceExpression(
                id.line,
                id.col,
                p.lineno(4),
                find_column(script, p.lexpos(4)) + 1,
                default,
                resources,
            )

    def p_resource(p: YaccProduction):
        r"resource : key LBRACKET resource_list RBRACKET"
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1].value):
            raise InvalidPuppetScript(f"Syntax error")
        if len(p[3]) == 1:
            p[0] = Resource(
                p[1].line,
                p[1].col,
                p.lineno(4),
                find_column(script, p.lexpos(4)) + 1,
                p[1],
                p[3][0][0],
                p[3][0][1],
            )
        else:
            resources = map(lambda r: Resource(r[2], r[3], r[4], r[5], p[1], r[0], r[1]), p[3])  # type: ignore
            default = None
            for r in resources:
                if isinstance(r.title, Value) and r.title.value == "default":
                    default = r
                    break
            resources = list(
                filter(
                    lambda r: isinstance(r.title, Value) and r.title.value != "default",
                    resources,
                )
            )

            p[0] = ResourceExpression(
                p[1].line,
                p[1].col,
                p.lineno(4),
                find_column(script, p.lexpos(4)) + 1,
                default,
                resources,
            )

    def p_resource_list(p: YaccProduction):
        r"resource_list : resource_body DOT_COMMA resource_list"
        p[0] = [p[1]] + p[3]

    def p_resource_list_single(p: YaccProduction):
        r"resource_list : resource_body"
        p[0] = [p[1]]

    def p_resource_list_empty(p: YaccProduction):
        r"resource_list : empty"
        p[0] = []

    def p_resource_body(p: YaccProduction):
        r"resource_body : expression COLON attributes"
        if len(p[3]) > 0:
            p[0] = (
                p[1],
                p[3],
                p.lineno(1),
                find_column(script, p.lexpos(1)),
                p[3][-1].end_line,
                p[3][-1].end_col,
            )
        else:
            p[0] = (
                p[1],
                p[3],
                p.lineno(1),
                find_column(script, p.lexpos(1)),
                p.lineno(2),
                find_column(script, p.lexpos(2)),
            )

    def p_virtual_resource(p: YaccProduction):
        r"resource : AT ID LBRACKET resource_list RBRACKET"
        if len(p[4]) == 1:
            p[0] = Resource(
                p.lineno(2),
                find_column(script, p.lexpos(2)),
                p.lineno(5),
                find_column(script, p.lexpos(5)) + 1,
                "@" + p[2],
                p[4][0][0],
                p[4][0][1],
            )
        else:
            resources = map(lambda r: Resource(r[2], r[3], r[4], r[5], "@" + p[2], r[0], r[1]), p[4])  # type: ignore
            default = None
            for r in resources:
                if isinstance(r.title, Value) and r.title.value == "default":
                    default = r
                    break
            resources = list(
                filter(
                    lambda r: isinstance(r.title, Value) and r.title.value != "default",
                    resources,
                )
            )

            p[0] = ResourceExpression(
                p.lineno(2),
                find_column(script, p.lexpos(2)),
                p.lineno(5),
                find_column(script, p.lexpos(5)) + 1,
                default,
                resources,
            )

    def p_exported_resource(p: YaccProduction):
        r"resource : AT AT ID LBRACKET resource_list RBRACKET"
        if len(p[4]) == 1:
            p[0] = Resource(
                p.lineno(3),
                find_column(script, p.lexpos(3)),
                p.lineno(6),
                find_column(script, p.lexpos(6)) + 1,
                "@@" + p[3],
                p[5][0][0],
                p[5][0][1],
            )
        else:
            resources = map(lambda r: Resource(r[2], r[3], r[4], r[5], "@@" + p[3], r[0], r[1]), p[5])  # type: ignore
            default = None
            for r in resources:
                if isinstance(r.title, Value) and r.title.value == "default":
                    default = r
                    break
            resources = list(
                filter(
                    lambda r: isinstance(r.title, Value) and r.title.value != "default",
                    resources,
                )
            )

            p[0] = ResourceExpression(
                p.lineno(3),
                find_column(script, p.lexpos(3)),
                p.lineno(6),
                find_column(script, p.lexpos(6)) + 1,
                default,
                resources,
            )

    def p_abstract_resource(p: YaccProduction):
        r"resource : reference LBRACKET expression COLON attributes RBRACKET"
        if p[1].type != "Resource":
            raise InvalidPuppetScript(f"Syntax error")
        p[0] = Resource(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(6),
            find_column(script, p.lexpos(6)) + 1,
            p[1],
            p[3],
            p[5],
        )

    def p_change_resource(p: YaccProduction):
        r"resource : reference LBRACKET attributes RBRACKET"
        p[0] = Resource(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(4),
            find_column(script, p.lexpos(4)) + 1,
            p[1],
            None,
            p[3],
        )

    def p_change_resource_collector(p: YaccProduction):
        r"resource : resource_collector LBRACKET attributes RBRACKET"
        p[0] = Resource(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(4),
            find_column(script, p.lexpos(4)) + 1,
            p[1],
            None,
            p[3],
        )

    def p_resource_default(p: YaccProduction):
        r"resource : ID_TYPE LBRACKET attributes RBRACKET"
        p[0] = Resource(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(4),
            find_column(script, p.lexpos(4)) + 1,
            p[1],
            None,
            p[3],
        )

    def p_resource_declaration(p: YaccProduction):
        r"resource : DEFINE ID LPAREN parameters RPAREN LBRACKET block RBRACKET"
        p[0] = ResourceDeclaration(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(8),
            find_column(script, p.lexpos(8)) + 1,
            p[2],
            p[4],
            p[7],
        )

    def p_resource_declaration_no_parameters(p: YaccProduction):
        r"resource : DEFINE ID LBRACKET block RBRACKET"
        p[0] = ResourceDeclaration(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2],
            [],
            p[4],
        )

    def p_resource_collector(p: YaccProduction):
        r"resource_collector : ID_TYPE LANGLEBRACKET rc_expression RANGLEBRACKET"
        p[0] = ResourceCollector(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(4),
            find_column(script, p.lexpos(4)) + 1,
            p[1],
            p[3],
        )

    def p_resource_collector_empty(p: YaccProduction):
        r"resource_collector : ID_TYPE LANGLEBRACKET RANGLEBRACKET"
        p[0] = ResourceCollector(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(3),
            find_column(script, p.lexpos(3)) + 1,
            p[1],
            None,
        )

    def p_resource_collector_expression_equal(p: YaccProduction):
        r"rc_expression : rc_expression CMP_EQUAL rc_expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )

    def p_resource_collector_expression_not_equal(p: YaccProduction):
        r"rc_expression : rc_expression CMP_NOT_EQUAL rc_expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )

    def p_resource_collector_expression_and(p: YaccProduction):
        r"rc_expression : rc_expression BOOL_AND rc_expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )

    def p_resource_collector_expression_or(p: YaccProduction):
        r"rc_expression : rc_expression BOOL_OR rc_expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )

    def p_resource_collector_expression_paren(p: YaccProduction):
        r"rc_expression : LPAREN rc_expression RPAREN"
        p[0] = p[2]

    def p_resource_collector_expression_value(p: YaccProduction):
        r"rc_expression : expression"
        p[0] = p[1]

    def p_parameters(p: YaccProduction):
        r"parameters : parameter COMMA parameters"
        p[0] = [p[1]] + p[3]

    def p_parameters_single(p: YaccProduction):
        r"parameters : parameter"
        p[0] = [p[1]]

    def p_parameters_empty(p: YaccProduction):
        r"parameters : empty"
        p[0] = []

    def p_parameter(p: YaccProduction):
        r"parameter : data_type ID EQUAL expression"
        p[0] = Parameter(
            p[1].line, p[1].col, p[4].end_line, p[4].end_col, p[1], p[2], p[4]
        )

    def p_parameter_no_default(p: YaccProduction):
        r"parameter : data_type ID"
        p[0] = Parameter(
            p[1].line,
            p[1].col,
            p.lineno(2),
            find_column(script, p.lexpos(2)) + len(p[2]),
            p[1],
            p[2],
            None,
        )

    def p_parameter_only_name(p: YaccProduction):
        r"parameter : ID"
        p[0] = Parameter(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            "",
            p[1],
            None,
        )

    def p_parameter_default_without_type(p: YaccProduction):
        r"parameter : ID EQUAL expression"
        p[0] = Parameter(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p[3].end_line,
            p[3].end_col,
            "",
            p[1],
            p[3],
        )

    def p_parameter_extra(p: YaccProduction):
        r"parameter : ID ARITH_MUL ID EQUAL expression"
        p[0] = Parameter(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p[5].end_line,
            p[5].end_col,
            p[1],
            p[2],
            p[4],
        )

    def p_parameter_no_default_extra(p: YaccProduction):
        r"parameter : ID ARITH_MUL ID"
        p[0] = Parameter(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(3),
            find_column(script, p.lexpos(3)) + len(p[3]),
            p[1],
            p[2],
            None,
        )

    def p_parameter_only_name_extra(p: YaccProduction):
        r"parameter : ARITH_MUL ID"
        p[0] = Parameter(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(2),
            find_column(script, p.lexpos(2)) + len(p[2]),
            "",
            p[1],
            None,
        )

    def p_parameter_default_without_type_extra(p: YaccProduction):
        r"parameter : ARITH_MUL ID EQUAL expression"
        p[0] = Parameter(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p[4].end_line,
            p[4].end_col,
            "",
            p[1],
            p[3],
        )

    def p_attributes(p: YaccProduction):
        r"attributes : attribute COMMA attributes"
        p[0] = [p[1]] + p[3]

    def p_attributes_single(p: YaccProduction):
        r"attributes : attribute"
        p[0] = [p[1]]

    def p_attributes_empty(p: YaccProduction):
        r"attributes : empty"
        p[0] = []

    def p_attribute(p: YaccProduction):
        r"attribute : ID HASH_ROCKET expression"
        id = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )
        p[0] = Attribute(id, p[3])

    def p_attribute_key(p: YaccProduction):
        r"attribute : key HASH_ROCKET expression"
        p[0] = Attribute(p[1], p[3])

    def p_attribute_splat(p: YaccProduction):
        r"attribute : ARITH_MUL HASH_ROCKET expression"
        id = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )
        p[0] = Attribute(id, p[3])

    def p_attribute_plussign(p: YaccProduction):
        r"attribute : ID PLUSIGNMENT expression"
        id = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )
        p[0] = Attribute(id, p[3])

    def p_attribute_key_plussign(p: YaccProduction):
        r"attribute : key PLUSIGNMENT expression"
        p[0] = Attribute(p[1], p[3])

    def p_attribute_splat_plussign(p: YaccProduction):
        r"attribute : ARITH_MUL PLUSIGNMENT expression"
        id = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )
        p[0] = Attribute(id, p[3])

    def p_key_default(p: YaccProduction):
        r"key : DEFAULT"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_node(p: YaccProduction):
        r"key : NODE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_site(p: YaccProduction):
        r"key : SITE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_import(p: YaccProduction):
        r"key : IMPORT"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_unless(p: YaccProduction):
        r"key : UNLESS"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_type(p: YaccProduction):
        r"key : TYPE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_include(p: YaccProduction):
        r"key : INCLUDE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_require(p: YaccProduction):
        r"key : REQUIRE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_contain(p: YaccProduction):
        r"key : CONTAIN"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_tag(p: YaccProduction):
        r"key : TAG"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_debug(p: YaccProduction):
        r"key : DEBUG"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_info(p: YaccProduction):
        r"key : INFO"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_notice(p: YaccProduction):
        r"key : NOTICE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_warning(p: YaccProduction):
        r"key : WARNING"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_err(p: YaccProduction):
        r"key : ERR"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_attributekey_fail(p: YaccProduction):
        r"key : FAIL"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_key_realize(p: YaccProduction):
        r"key : REALIZE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_array(p: YaccProduction):
        r"array : LPARENR expressionlist RPARENR"
        p[0] = Array(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(3),
            find_column(script, p.lexpos(3)) + 1,
            p[2],
        )

    def p_hash(p: YaccProduction):
        r"hash : LBRACKET keyvalue_pairs RBRACKET"
        res: Dict[CodeElement, CodeElement] = {}
        for kv in p[2]:
            res[kv[0]] = kv[1]
        p[0] = Hash(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(3),
            find_column(script, p.lexpos(3)) + 1,
            res,
        )

    def p_keyvalue_pairs(p: YaccProduction):
        r"keyvalue_pairs : keyvalue COMMA keyvalue_pairs"
        p[0] = [p[1]] + p[3]

    def p_keyvalue_pairs_single(p: YaccProduction):
        r"keyvalue_pairs : keyvalue"
        p[0] = [p[1]]

    def p_keyvalue_pairs_empty(p: YaccProduction):
        r"keyvalue_pairs : empty"
        p[0] = []

    def p_keyvalue(p: YaccProduction):
        r"keyvalue : expression HASH_ROCKET expression"
        p[0] = (p[1], p[3])

    def p_keyvalue_key(p: YaccProduction):
        r"keyvalue : key HASH_ROCKET expression"
        p[0] = (p[1], p[3])

    def p_expressionlist(p: YaccProduction):
        r"expressionlist : expression COMMA expressionlist"
        p[0] = [p[1]] + p[3]
        p.set_lineno(0, p.lineno(1))

    def p_expressionlist_single(p: YaccProduction):
        r"expressionlist : expression"
        p[0] = [p[1]]
        p.set_lineno(0, p.lineno(1))

    def p_expressionlist_empty(p: YaccProduction):
        r"expressionlist : empty"
        p[0] = []

    ### Expressions ###
    def p_expression(p: YaccProduction):
        "expression : value"
        p[0] = p[1]
        p.set_lineno(0, p[1].line)

    def p_expression_function_call(p: YaccProduction):
        r"expression : function_call"
        p[0] = p[1]
        p.set_lineno(0, p[1].line)

    def p_expression_statement_function(p: YaccProduction):
        "expression : statement_function"
        p[0] = p[1]
        p.set_lineno(0, p[1].line)

    def p_expression_paren(p: YaccProduction):
        "expression : LPAREN expression RPAREN"
        p[0] = p[2]
        p.set_lineno(0, p.lineno(1))

    def p_expression_assignment(p: YaccProduction):
        r"expression : assignment"
        p[0] = p[1]
        p.set_lineno(0, p[1].line)

    def p_expression_access_section(p: YaccProduction):
        r"expression : expression LPARENR INTEGER COMMA INTEGER RPARENR"
        p[0] = Operation(
            p[1].line,
            p[1].col,
            p.lineno(6),
            find_column(script, p.lexpos(6)) + 1,
            (p[1], p[3], p[5]),
            p[2] + p[4] + p[6],
        )
        p.set_lineno(0, p.lineno(1))

    ## Selector ##
    def p_expression_selector(p: YaccProduction):
        r"expression : expression QUESTION_MARK hash"
        p[0] = Selector(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p[3].end_line,
            p[3].end_col,
            p[1],
            p[3],
        )
        p.set_lineno(0, p.lineno(1))

    ## Comparison ##
    def p_expression_equal(p: YaccProduction):
        r"expression : expression CMP_EQUAL expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_not_equal(p: YaccProduction):
        r"expression : expression CMP_NOT_EQUAL expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_less_than(p: YaccProduction):
        r"expression : expression CMP_LESS_THAN expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_greater_than(p: YaccProduction):
        r"expression : expression CMP_GREATER_THAN expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_less_than_or_equal(p: YaccProduction):
        r"expression : expression CMP_LESS_THAN_OR_EQUAL expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_greater_than_or_equal(p: YaccProduction):
        r"expression : expression CMP_GREATER_THAN_OR_EQUAL expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_regex_match(p: YaccProduction):
        r"expression : expression CMP_REGEX_MATCH expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_regex_not_match(p: YaccProduction):
        r"expression : expression CMP_REGEX_NOT_MATCH expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_in(p: YaccProduction):
        r"expression : expression CMP_IN expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    ## Boolean
    def p_expression_and(p: YaccProduction):
        r"expression : expression BOOL_AND expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_or(p: YaccProduction):
        r"expression : expression BOOL_OR expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_not(p: YaccProduction):
        r"expression : BOOL_NOT expression"
        p[0] = Operation(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p[2].end_line,
            p[2].end_col,
            (p[2],),
            p[1],
        )
        p.set_lineno(0, p.lineno(1))

    ## Arithmetic
    def p_expression_negation(p: YaccProduction):
        r"expression : ARITH_SUB expression %prec ARITH_MINUS"
        p[0] = Operation(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p[2].end_line,
            p[2].end_col,
            (p[2],),
            p[1],
        )
        p.set_lineno(0, p.lineno(1))

    # It also works for array concatenation and hash merging
    def p_expression_addition(p: YaccProduction):
        r"expression : expression ARITH_ADD expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    # It also works for array and hash removal
    def p_expression_subtraction(p: YaccProduction):
        r"expression : expression ARITH_SUB expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_division(p: YaccProduction):
        r"expression : expression ARITH_DIV expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_multiplication(p: YaccProduction):
        r"expression : expression ARITH_MUL expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_modulo(p: YaccProduction):
        r"expression : expression ARITH_MOD expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    # It also works for array append
    def p_expression_left_shift(p: YaccProduction):
        r"expression : expression ARITH_LSHIFT expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_right_shift(p: YaccProduction):
        r"expression : expression ARITH_RSHIFT expression"
        p[0] = Operation(
            p[1].line, p[1].col, p[3].end_line, p[3].end_col, (p[1], p[3]), p[2]
        )
        p.set_lineno(0, p.lineno(1))

    ## Array Operations
    def p_expression_splat(p: YaccProduction):
        r"expression : ARITH_MUL expression %prec ARRAY_SPLAT"
        p[0] = Operation(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p[2].end_line,
            p[2].end_col,
            (p[2],),
            p[1],
        )
        p.set_lineno(0, p.lineno(1))

    def p_expression_access(p: YaccProduction):
        r"expression : access"
        p[0] = p[1]
        p.set_lineno(0, p.lineno(1))

    def p_access(p: YaccProduction):
        r"access : expression LPARENR expressionlist RPARENR"
        p[0] = Operation(
            p[1].line,
            p[1].col,
            p.lineno(4),
            find_column(script, p.lexpos(4)) + 1,
            (p[1], p[3]),
            p[2] + p[4],
        )
        p.set_lineno(0, p.lineno(1))

    ## Reference
    def p_expression_reference(p: YaccProduction):
        r"expression : reference"
        p[0] = p[1]
        p.set_lineno(0, p[1].line)

    def p_reference(p: YaccProduction):
        r"reference : ID_TYPE LPARENR expressionlist RPARENR"
        p[0] = Reference(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(4),
            find_column(script, p.lexpos(4)) + 1,
            p[1],
            p[3],
        )

    # Function calls
    def p_statement_function(p: YaccProduction):
        r"statement_function : key expressionlist"
        if len(p[2]) > 0:
            p[0] = globals()[statement_functions_class[p[1].value]](
                p[1].line, p[1].col, p[2][-1].end_line, p[2][-1].end_col, p[2]
            )
        else:
            p[0] = globals()[statement_functions_class[p[1].value]](
                p[1].line, p[1].col, p[1].line, p[1].col + len(p[1]), p[2]
            )

    def p_statement_function_paren(p: YaccProduction):
        r"statement_function : key LPAREN expressionlist RPAREN"
        p[0] = globals()[statement_functions_class[p[1].value]](
            p[1].line, p[1].col, p.lineno(4), find_column(script, p.lexpos(4)) + 1, p[3]
        )

    def p_function_call_prefix(p: YaccProduction):
        r"function_call : ID LPAREN expressionlist RPAREN %prec NO_LAMBDA"
        id = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )
        p[0] = FunctionCall(
            id.line,
            id.col,
            p.lineno(4),
            find_column(script, p.lexpos(4)) + 1,
            id,
            p[3],
            None,
        )

    def p_function_call_type(p: YaccProduction):
        r"function_call : TYPE LPAREN expressionlist RPAREN %prec NO_LAMBDA"
        id = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )
        p[0] = FunctionCall(
            id.line,
            id.col,
            p.lineno(4),
            find_column(script, p.lexpos(4)) + 1,
            id,
            p[3],
            None,
        )

    def p_function_call_id_type(p: YaccProduction):
        r"function_call : ID_TYPE LPAREN expressionlist RPAREN %prec NO_LAMBDA"
        id = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )
        p[0] = FunctionCall(
            id.line,
            id.col,
            p.lineno(4),
            find_column(script, p.lexpos(4)) + 1,
            id,
            p[3],
            None,
        )

    def p_function_call_prefix_lambda(p: YaccProduction):
        r"function_call : ID LPAREN expressionlist RPAREN lambda %prec LAMBDA"
        id = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )
        p[0] = FunctionCall(
            id.line,
            id.col,
            p.lineno(4),
            find_column(script, p.lexpos(4)) + 1,
            id,
            p[3],
            p[5],
        )

    def p_function_call_chained(p: YaccProduction):
        r"function_call : expression DOT ID %prec NO_LAMBDA"
        id = Value(
            p.lineno(3),
            find_column(script, p.lexpos(3)),
            p.lineno(3),
            find_column(script, p.lexpos(3)) + len(p[3]),
            p[3],
        )
        p[0] = FunctionCall(
            id.line,
            id.col,
            p.lineno(3),
            find_column(script, p.lexpos(3)) + len(p[3]),
            id,
            [p[1]],
            None,
        )

    def p_function_call_chained_args(p: YaccProduction):
        r"function_call : expression DOT ID LPAREN expressionlist RPAREN %prec NO_LAMBDA"
        id = Value(
            p.lineno(3),
            find_column(script, p.lexpos(3)),
            p.lineno(3),
            find_column(script, p.lexpos(3)) + len(p[3]),
            p[3],
        )
        p[0] = FunctionCall(
            id.line,
            id.col,
            p.lineno(6),
            find_column(script, p.lexpos(6)) + 1,
            id,
            [p[1]] + p[5],
            None,
        )

    def p_function_call_chained_lambda(p: YaccProduction):
        r"function_call : expression DOT ID lambda %prec LAMBDA"
        id = Value(
            p.lineno(3),
            find_column(script, p.lexpos(3)),
            p.lineno(3),
            find_column(script, p.lexpos(3)) + len(p[3]),
            p[3],
        )
        p[0] = FunctionCall(
            id.line, id.col, p[4].end_line, p[4].end_col, id, [p[1]], p[4]
        )

    def p_function_call_chained_lambda_args(p: YaccProduction):
        r"function_call : expression DOT ID LPAREN expressionlist RPAREN lambda %prec LAMBDA"
        id = Value(
            p.lineno(3),
            find_column(script, p.lexpos(3)),
            p.lineno(3),
            find_column(script, p.lexpos(3)) + len(p[3]),
            p[3],
        )
        p[0] = FunctionCall(
            id.line, id.col, p[7].end_line, p[7].end_col, id, [p[1]] + p[5], p[7]
        )

    def p_lambda(p: YaccProduction):
        r"lambda : BAR parameters BAR LBRACKET block RBRACKET"
        p[0] = Lambda(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(6),
            find_column(script, p.lexpos(6)) + 1,
            p[2],
            p[5],
        )

    def p_sensitive(p: YaccProduction):
        r"function_call : SENSITIVE LPAREN STRING RPAREN"
        p[0] = FunctionCall(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(4),
            find_column(script, p.lexpos(4)) + 1,
            p[1],
            [p[3]],
            None,
        )

    def p_sensitive_id(p: YaccProduction):
        r"function_call : SENSITIVE DOT ID LPAREN STRING RPAREN"
        p[0] = FunctionCall(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(6),
            find_column(script, p.lexpos(6)) + 1,
            p[1],
            [p[5]],
            None,
        )

    # Chaining arrows
    def p_chaining_left(p: YaccProduction):
        "chaining : chaining_value CHAINING_LEFT chaining_value"
        p[0] = Chaining(p[1], p[3], p[2])

    def p_chaining_right(p: YaccProduction):
        "chaining : chaining_value CHAINING_RIGHT chaining_value"
        p[0] = Chaining(p[1], p[3], p[2])

    def p_chaining_value(p: YaccProduction):
        "chaining_value : chaining"
        p[0] = p[1]

    def p_chaining_value_array(p: YaccProduction):
        "chaining_value : referencelist"
        if len(p[1]) == 1:
            p[0] = p[1][0]
        else:
            p[0] = p[1]

    def p_chaining_value_resource(p: YaccProduction):
        "chaining_value : resource"
        p[0] = p[1]

    def p_chaining_value_class(p: YaccProduction):
        "chaining_value : class"
        p[0] = p[1]

    def p_chaining_value_case(p: YaccProduction):
        "chaining_value : case"
        p[0] = p[1]

    def p_chaining_value_id(p: YaccProduction):
        "chaining_value : value"
        p[0] = p[1]

    def p_chaining_value_collector(p: YaccProduction):
        "chaining_value : resource_collector"
        p[0] = p[1]

    def p_referencelist(p: YaccProduction):
        r"referencelist : reference COMMA referencelist"
        p[0] = [p[1]] + p[3]

    def p_referencelist_single(p: YaccProduction):
        r"referencelist : reference"
        p[0] = [p[1]]

    ### Statements ###
    # The statements are here because they need to be below the expressions
    # in order to have the correct behaviour when solving the reduce/reduce conflicts
    def p_statement_func(p: YaccProduction):
        r"statement : function"
        p[0] = p[1]

    def p_statement_function_call(p: YaccProduction):
        r"statement : function_call"
        p[0] = p[1]

    def p_statement_assignment(p: YaccProduction):
        r"statement : assignment"
        p[0] = p[1]

    def p_statement_node(p: YaccProduction):
        r"statement : node"
        p[0] = p[1]

    def p_statement_resource(p: YaccProduction):
        r"statement : resource"
        p[0] = p[1]

    def p_statement_resource_collector(p: YaccProduction):
        r"statement : resource_collector"
        p[0] = p[1]

    def p_statement_class(p: YaccProduction):
        r"statement : class"
        p[0] = p[1]

    def p_statement_if(p: YaccProduction):
        r"statement : if"
        p[0] = p[1]

    def p_statement_unless(p: YaccProduction):
        r"statement : unless"
        p[0] = p[1]

    def p_statement_case(p: YaccProduction):
        r"statement : case"
        p[0] = p[1]

    def p_statement_chaining(p: YaccProduction):
        r"statement : chaining"
        p[0] = p[1]

    def p_statement_statement_function_function(p: YaccProduction):
        r"statement : statement_function"
        p[0] = p[1]

    # Function declaration
    def p_function(p: YaccProduction):
        r"function : FUNCTION ID LPAREN parameters RPAREN LBRACKET block RBRACKET"
        p[0] = Function(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(8),
            find_column(script, p.lexpos(8)) + 1,
            p[2],
            p[4],
            None,
            p[7],
        )

    def p_function_return(p: YaccProduction):
        r"function : FUNCTION ID LPAREN parameters RPAREN ARITH_RSHIFT data_type LBRACKET block RBRACKET"
        p[0] = Function(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(10),
            find_column(script, p.lexpos(10)) + 1,
            p[2],
            p[4],
            p[7],
            p[9],
        )

    # Conditional statements
    def p_if(p: YaccProduction):
        r"if : IF expression LBRACKET block RBRACKET"
        p[0] = If(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2],
            p[4],
            None,
        )

    def p_if_elsif(p: YaccProduction):
        r"if : IF expression LBRACKET block RBRACKET elsif"
        p[0] = If(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2],
            p[4],
            p[6],
        )

    def p_elif(p: YaccProduction):
        r"elsif : ELSIF expression LBRACKET block RBRACKET"
        p[0] = If(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2],
            p[4],
            None,
        )

    def p_elif_elif(p: YaccProduction):
        r"elsif : ELSIF expression LBRACKET block RBRACKET elsif"
        p[0] = If(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2],
            p[4],
            p[6],
        )

    def p_else(p: YaccProduction):
        r"elsif : ELSE LBRACKET block RBRACKET"
        p[0] = If(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(4),
            find_column(script, p.lexpos(4)) + 1,
            None,
            p[3],
            None,
        )

    def p_unless(p: YaccProduction):
        r"unless : UNLESS expression LBRACKET block RBRACKET"
        p[0] = Unless(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2],
            p[4],
            None,
        )

    def p_unless_else(p: YaccProduction):
        r"unless : UNLESS expression LBRACKET block RBRACKET ELSE LBRACKET block RBRACKET"
        un_else = Unless(
            p.lineno(6),
            find_column(script, p.lexpos(6)),
            p.lineno(9),
            find_column(script, p.lexpos(9)) + 1,
            None,
            p[8],
            None,
        )
        p[0] = Unless(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2],
            p[4],
            un_else,
        )

    def p_case(p: YaccProduction):
        r"case : CASE expression LBRACKET matches RBRACKET"
        p[0] = Case(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[2],
            p[4],
        )

    def p_matches(p: YaccProduction):
        r"matches : match matches"
        p[0] = [p[1]] + p[2]

    def p_matches_empty(p: YaccProduction):
        r"matches : empty"
        p[0] = []

    def p_match(p: YaccProduction):
        r"match : expressionlist COLON LBRACKET block RBRACKET"
        p[0] = Match(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(5),
            find_column(script, p.lexpos(5)) + 1,
            p[1],
            p[4],
        )

    ### Data Type ###
    def p_data_type(p: YaccProduction):
        r"data_type : ID_TYPE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_data_type_reference(p: YaccProduction):
        r"data_type : reference"
        p[0] = p[1]

    ### Values ###
    def p_value_hash(p: YaccProduction):
        r"value : hash"
        p[0] = p[1]

    def p_value_array(p: YaccProduction):
        r"value : array"
        p[0] = p[1]

    def p_value_string(p: YaccProduction):
        r"value : STRING"
        start_line = p.lineno(1)
        end_line = start_line + p[1].count("\n")
        start_col = find_column(script, p.lexpos(1))
        if start_line == end_line:
            end_col = start_col + len(p[1].split("\n")[-1]) + 2
        else:
            end_col = len(p[1].split("\n")[-1]) + 2
        p[0] = Value(start_line, start_col, end_line, end_col, p[1])

    def p_value_string_docs(p: YaccProduction):
        r"value : AT LPAREN STRING ARITH_DIV ID_TYPE RPAREN start_docs STRING BAR ID_TYPE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(10),
            find_column(script, p.lexpos(10)) + len(p[10]),
            p[8],
        )

    def p_value_string_docs_sub(p: YaccProduction):
        r"value : AT LPAREN STRING ARITH_DIV ID_TYPE RPAREN start_docs STRING BAR ARITH_SUB ID_TYPE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(11),
            find_column(script, p.lexpos(11)) + len(p[10]),
            p[8],
        )

    def p_value_string_docs_syntax(p: YaccProduction):
        r"value : AT LPAREN STRING COLON ID ARITH_DIV ID_TYPE RPAREN start_docs STRING BAR ID_TYPE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(12),
            find_column(script, p.lexpos(12)) + len(p[10]),
            p[10],
        )

    def p_value_string_docs_syntax_sub(p: YaccProduction):
        r"value : AT LPAREN STRING COLON ID ARITH_DIV ID_TYPE RPAREN start_docs STRING BAR ARITH_SUB ID_TYPE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(13),
            find_column(script, p.lexpos(13)) + len(p[10]),
            p[10],
        )

    def p_value_string_docs_id(p: YaccProduction):
        r"value : AT LPAREN STRING ARITH_DIV ID_TYPE RPAREN start_docs STRING BAR ID"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(10),
            find_column(script, p.lexpos(10)) + len(p[10]),
            p[8],
        )

    def p_value_string_docs_sub_id(p: YaccProduction):
        r"value : AT LPAREN STRING ARITH_DIV ID RPAREN start_docs STRING BAR ARITH_SUB ID_TYPE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(11),
            find_column(script, p.lexpos(11)) + len(p[10]),
            p[8],
        )

    def p_value_string_docs_syntax_id(p: YaccProduction):
        r"value : AT LPAREN STRING COLON ID ARITH_DIV ID RPAREN start_docs STRING BAR ID_TYPE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(12),
            find_column(script, p.lexpos(12)) + len(p[10]),
            p[10],
        )

    def p_value_string_docs_syntax_sub_id(p: YaccProduction):
        r"value : AT LPAREN STRING COLON ID ARITH_DIV ID RPAREN start_docs STRING BAR ARITH_SUB ID_TYPE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(13),
            find_column(script, p.lexpos(13)) + len(p[10]),
            p[10],
        )

    def p_start_docs(p: YaccProduction):
        r"start_docs :"
        lexer.begin("docs")

    def p_value_false(p: YaccProduction):
        r"value : FALSE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            False,
        )

    def p_value_true(p: YaccProduction):
        r"value : TRUE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            True,
        )

    def p_value_integer(p: YaccProduction):
        r"value : INTEGER"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(str(p[1])),
            int(p[1]),
        )

    def p_value_float(p: YaccProduction):
        r"value : FLOAT"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(str(p[1])),
            float(p[1]),
        )

    def p_value_id(p: YaccProduction):
        r"value : ID"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_value_type_id(p: YaccProduction):
        r"value : ID_TYPE"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_value_undef(p: YaccProduction):
        r"value : UNDEF"
        p[0] = Value(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(1),
            find_column(script, p.lexpos(1)) + len(p[1]),
            p[1],
        )

    def p_value_stat_func(p: YaccProduction):
        r"value : key"
        p[0] = p[1]

    def p_value_regex(p: YaccProduction):
        r"value : regex"
        p[0] = p[1]

    def p_regex(p: YaccProduction):
        r"regex : ARITH_DIV start_regex REGEXPRESSION ARITH_DIV"
        p[0] = Regex(
            p.lineno(1),
            find_column(script, p.lexpos(1)),
            p.lineno(4),
            find_column(script, p.lexpos(4)),
            p[3],
        )

    def p_start_regex(p: YaccProduction):
        r"start_regex :"
        lexer.begin("regex")

    def p_empty(p: YaccProduction):
        r"empty :"

    def p_error(p: YaccProduction):
        raise InvalidPuppetScript(f"Syntax error {p}")

    # Build the parser
    parsedir = os.path.dirname(pf.__file__)
    # By default, store generated parse files with the code
    # If we don't have write permission, put them in the configured tempdir
    if not os.access(parsedir, os.W_OK):
        parsedir = tempfile.gettempdir()

    parser = yacc(debug=False, outputdir=parsedir)
    return parser.parse(script), comments
