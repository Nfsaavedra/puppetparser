from ply.lex import lex
from ply.yacc import yacc
import re
from puppetparser.model import Assignment, Attribute, Case, Chaining, Comment, Contain, Debug, Fail, Function, FunctionCall, If, Include, Lambda, Match, Node, Operation, Parameter, PuppetClass, Realize, Reference, Regex, Require, Resource, ResourceCollector, ResourceDeclaration, ResourceExpression, Selector, Tag, Unless

def find_column(input, pos):
    line_start = input.rfind('\n', 0, pos) + 1
    return (pos - line_start) + 1

def parser_yacc(script):
    comments = []

    tokens = (
        # Keywords
        'APPLICATION', 
        'ATTR', 
        'CASE',
        'COMPONENT', 
        'CONSUMES', 
        'DEFAULT', 
        'DEFINE', 
        'ELSIF',
        'ELSE',
        'FALSE',
        'FUNCTION',
        'IF',
        'IMPORT',
        'IN',
        'INHERITS',
        'NODE',
        'PRIVATE',
        'PRODUCES',
        'REGEXP',
        'SITE',
        'TRUE',
        'TYPE',
        'UNDEF',
        'UNIT',
        'UNLESS',
        # Values
        'STRING',
        'INTEGER',
        'FLOAT',
        'REGEX',
        # SUGAR SYNTAX
        'LBRACKET',
        'RBRACKET',
        'LANGLEBRACKET',
        'RANGLEBRACKET',
        'LPAREN',
        'RPAREN',
        'LPARENR',
        'RPARENR',
        'EQUAL',
        'COLON',
        'HASH_ROCKET',
        'COMMA',
        'BAR',
        'DOT',
        'QUESTION_MARK',
        'AT',
        'DOT_COMMA',
        # Identifiers
        'ID',
        'ID_TYPE',
        'SENSITIVE',
        # Special
        'CLASS',
        # Comparison operators
        'CMP_EQUAL',
        'CMP_NOT_EQUAL',
        'CMP_LESS_THAN',
        'CMP_GREATER_THAN',
        'CMP_LESS_THAN_OR_EQUAL',
        'CMP_GREATER_THAN_OR_EQUAL',
        'CMP_REGEX_MATCH',
        'CMP_REGEX_NOT_MATCH',
        'CMP_IN',
        # Boolean operators
        'BOOL_AND',
        'BOOL_OR',
        'BOOL_NOT',
        # Arithmetic operators
        'ARITH_ADD',
        'ARITH_SUB',
        'ARITH_DIV',
        'ARITH_MUL',
        'ARITH_MOD',
        'ARITH_LSHIFT',
        'ARITH_RSHIFT',
        # Statement functions
        'INCLUDE',
        'REQUIRE',
        'CONTAIN',
        'TAG',
        'DEBUG',
        'INFO',
        'NOTICE',
        'WARNING',
        'ERR',
        'FAIL',
        'REALIZE',
        # Chaining arrows
        'CHAINING_LEFT',
        'CHAINING_RIGHT'
    )

    statement_functions = {
        'include' : 'INCLUDE',
        'require' : 'REQUIRE',
        'contain' : 'CONTAIN',
        'tag' : 'TAG',
        'debug' : 'DEBUG',
        'info' : 'INFO',
        'notice' : 'NOTICE',
        'warning' : 'WARNING',
        'err' : 'ERR',
        'fail' : 'FAIL',
        'realize' : 'REALIZE'
    }

    keywords = {
        'and': 'BOOL_AND', 
        'application': 'APPLICATION', 
        'attr': 'ATTR', 
        'case': 'CASE', 
        'component': 'COMPONENT', 
        'consumes': 'CONSUMES', 
        'default': 'DEFAULT', 
        'define': 'DEFINE', 
        'elsif': 'ELSIF',
        'else': 'ELSE',
        'false': 'FALSE',
        'function': 'FUNCTION',
        'if': 'IF',
        'import': 'IMPORT',
        'in': 'CMP_IN',
        'inherits': 'INHERITS',
        'node': 'NODE',
        'or': 'BOOL_OR',
        'private': 'PRIVATE',
        'produces': 'PRODUCES',
        'regexp': 'REGEXP',
        'site': 'SITE',
        'true': 'TRUE',
        'type': 'TYPE',
        'undef': 'UNDEF',
        'unit': 'UNIT',
        'unless': 'UNLESS',
        'class': 'CLASS',
    }

    states = (
        ('comment', 'exclusive'),
    )

    # Other
    t_LBRACKET = r'\{'
    t_RBRACKET = r'\}'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LPARENR = r'\['
    t_RPARENR = r'\]'
    t_QUESTION_MARK = r'\?'
    t_BAR = r'\|'
    t_AT = r'@'
    t_HASH_ROCKET = r'=>'
    t_COLON = r'\:'
    t_COMMA = r','
    t_DOT_COMMA = r';'
    t_DOT = r'\.'
    t_REGEX = r'\/.*\/'
    t_CMP_EQUAL = r'=='
    t_CMP_NOT_EQUAL = r'!='
    t_CMP_LESS_THAN = r'<'
    t_CMP_GREATER_THAN = r'>'
    t_CMP_LESS_THAN_OR_EQUAL = r'<='
    t_CMP_GREATER_THAN_OR_EQUAL = r'>='
    t_CMP_REGEX_MATCH = r'=~'
    t_CMP_REGEX_NOT_MATCH = r'!~'
    t_EQUAL = r'\='
    t_BOOL_NOT = r'!'
    t_ARITH_ADD = r'\+'
    t_ARITH_SUB = r'-'
    t_ARITH_DIV = r'\/'
    t_ARITH_MUL = r'\*'
    t_ARITH_MOD = r'%'
    t_ARITH_LSHIFT = r'<<'
    t_ARITH_RSHIFT = r'>>'
    t_CHAINING_RIGHT = r'->|~>'
    t_CHAINING_LEFT = r'<-|<~'
    t_LANGLEBRACKET = r'\<\|'
    t_RANGLEBRACKET = r'\|\>'

    # Identifiers
    t_ignore_ANY = r'[\t\ ]'

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_COMMENT(t):
        r'\#.*\n'
        comments.append(Comment(t.lexer.lineno, 
                find_column(script, t.lexpos), t.value[1:-1]))
        t.lexer.lineno += 1

    def t_comment(t):
        r'/\*'
        t.lexer.begin('comment')

    def t_comment_END(t):
        r'\*/'
        t.lexer.begin('INITIAL')

    def t_comment_content(t):
        r'[^(\*/)]+'
        comments.append(Comment(t.lexer.lineno, 
            find_column(script, t.lexpos), t.value))
        t.lexer.lineno += t.value.count('\n')

    def t_octal_INTEGER(t):
        r'0[0-9]+'
        t.value = int(t.value, 8)
        t.type = "INTEGER"
        return t

    def t_hexa_INTEGER(t):
        r'0x[0-9a-f]+'
        t.value = int(t.value, 16)
        t.type = "INTEGER"
        return t

    def t_NUMBER(t):
        r'((0|[1-9]\d*)(\.\d+)?(e-?(0|[1-9]\d*))?)'
        if '.' in t.value:
            t.type = "FLOAT"
        else:
            t.type = "INTEGER"
        return t

    def t_ID(t):
        r'[a-z\$]((::)?[a-z0-9\_\-]*)*'
        t.type = keywords.get(t.value, statement_functions.get(t.value,'ID'))
        return t

    def t_ID_TYPE(t):
        r'[A-Z\$]((::)?[a-z0-9\_\-]*)*'
        if t.value == 'Sensitive':
            t.type = 'SENSITIVE'
        return t

    def t_STRING(t):
        r"(\'([^\\\n]|(\\.))*?\')|(\"([^\\\n]|(\\.))*?\")"
        t.value = t.value[1:-1]
        return t

    def t_ANY_error(t):
        print(f'Illegal character {t.value[0]!r} ({t.lineno}, {find_column(script, t.lexpos)}).')
        t.lexer.skip(1)

    lexer = lex()
    # Give the lexer some input
    lexer.input(script)

    # while True:
    #     tok = lexer.token()
    #     if not tok: 
    #         break      # No more input
    #     print(tok)

    precedence = (
        ('nonassoc', 'NO_LAMBDA'),
        ('nonassoc', 'LAMBDA'),
        ('right', 'CHAINING_RIGHT'),
        ('right', 'CHAINING_LEFT'),
        ('left', 'EQUAL'),
        ('left', 'QUESTION_MARK'),
        ('left', 'DOT'),
        ('left', 'BOOL_OR'),
        ('left', 'BOOL_AND'),
        ('nonassoc', 'CMP_LESS_THAN', 'CMP_GREATER_THAN', 'CMP_LESS_THAN_OR_EQUAL', 'CMP_GREATER_THAN_OR_EQUAL'),
        ('nonassoc', 'CMP_EQUAL', 'CMP_NOT_EQUAL'),
        ('left', 'ARITH_LSHIFT', 'ARITH_RSHIFT'),
        ('left', 'ARITH_ADD', 'ARITH_SUB'),
        ('left', 'ARITH_MUL', 'ARITH_DIV', 'ARITH_MOD'),
        ('left', 'CMP_REGEX_MATCH', 'CMP_REGEX_NOT_MATCH'),
        ('left', 'CMP_IN'),
        ('right', 'ARRAY_SPLAT'),
        ('right', 'ARITH_MINUS'),
        ('right', 'BOOL_NOT'),
        ('right', 'LPARENR'),
        ('left', 'LPAREN'),
        ('left', 'BAR'),
    )

    start = 'program'

    def p_program(p):
        "program : block"
        p[0] = p[1]

    def p_class(p):
        r'class : CLASS class_header LBRACKET block RBRACKET'
        p[0] = PuppetClass(p.lineno(1), 
                find_column(script, p.lexpos(1)), p[2][0], p[4], p[2][2], p[2][1])

    def p_class_header(p):
        r'class_header : ID LPAREN parameters RPAREN'
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        p[0] = (p[1], p[3], "")

    def p_class_header_no_parameters(p):
        r'class_header : ID'
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        p[0] = (p[1], [], "")

    def p_class_header_inherits(p):
        r'class_header : ID LPAREN parameters RPAREN INHERITS ID'
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[6]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        p[0] = (p[1], p[3], p[6])

    def p_class_resource_declaration(p):
        r'class : CLASS LBRACKET expression COLON attributes RBRACKET'
        p[0] = PuppetClass(p.lineno(1), find_column(script, p.lexpos(1)),
                p[3], None, None, p[5])

    def p_node(p):
        r'node : NODE STRING LBRACKET block RBRACKET'
        p[0] = Node(p.lineno(1), find_column(script, p.lexpos(1)),  p[2], p[4])

    def p_node_regex(p):
        r'node : NODE REGEX LBRACKET block RBRACKET'
        p[0] = Node(p.lineno(1), find_column(script, p.lexpos(1)), p[2], p[4])

    def p_node_default(p):
        r'node : NODE DEFAULT LBRACKET block RBRACKET'
        p[0] = Node(p.lineno(1), find_column(script, p.lexpos(1)), p[2], p[4])

    def p_assignment(p):
        r'assignment : ID EQUAL expression'
        if not re.match(r"^\$[a-z0-9_][a-zA-Z0-9_]*$", p[1]) and not \
                re.match(r"^\$([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*::[a-z0-9_][a-zA-Z0-9_]*$", p[1]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value!r}.')
        p[0] = Assignment(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[3])

    def p_assignment_array(p):
        r'assignment : array EQUAL array'
        if len(p[1]) != len(p[3]):
            print(f'Syntax error on line {p.lineno(1)}. Arrays must match sizes.')
        for id in p[1]:
            if not re.match(r"^\$[a-z0-9_][a-zA-Z0-9_]*$", id) and not \
                    re.match(r"^\$([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*::[a-z0-9_][a-zA-Z0-9_]*$", id):
                print(f'Syntax error on line {p.lineno(1)}: {p.value!r}.')
        p[0] = Assignment(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[3])

    def p_assignment_hash(p):
        r'assignment : array EQUAL hash'
        for id in p[1]:
            if not re.match(r"^\$[a-z0-9_][a-zA-Z0-9_]*$", id) and not \
                    re.match(r"^\$([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*::[a-z0-9_][a-zA-Z0-9_]*$", id):
                print(f'Syntax error on line {p.lineno(1)}: {p.value!r}.')

            if id not in p[3]:
                print(f'Syntax error on line {p.lineno(1)}. The key must be present on the hash.')

        p[0] = Assignment(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[3])

    def p_block(p):
        r'block : statement block'
        p[0] = [p[1]] + p[2]

    def p_block_return(p):
        r'block : expression'
        p[0] = [p[1]]

    def p_block_empty(p):
        r'block : empty'
        p[0] = []

    def p_resource(p):
        r'resource : ID LBRACKET resource_body RBRACKET'
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        p[0] = Resource(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[3][0], p[3][1])

    def p_resource_expression(p):
        r'resource : ID LBRACKET resource_list RBRACKET'
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        resources = map(lambda r: Resource(r[2], r[3], p[1], r[0], r[2]), p[3])
        default = None
        for r in resources:
            if r.title == "default":
                default = r
                break
        resources = list(filter(lambda r: r.title != default, resources))

        p[0] = ResourceExpression(p.lineno(1), find_column(script, p.lexpos(1)), default, resources)

    def p_resource_list(p):
        r'resource_list : resource_body DOT_COMMA resource_list'
        p[0] = [p[1]] + p[3]

    def p_resource_list_single(p):
        r'resource_list : resource_body'
        p[0] = [p[1]]

    def p_resource_list_empty(p):
        r'resource_list : empty'
        p[0] = []

    def p_resource_body(p):
        r'resource_body : expression COLON attributes'
        p[0] = (p[1], p[3], p.lineno(1), find_column(script, p.lexpos(1)))

    def p_virtual_resource(p):
        r'resource : AT ID LBRACKET expression COLON attributes RBRACKET'
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        p[0] = Resource(p.lineno(1), find_column(script, p.lexpos(1)), "@" + p[2], p[4], p[6])

    def p_exported_resource(p):
        r'resource : AT AT ID LBRACKET expression COLON attributes RBRACKET'
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        p[0] = Resource(p.lineno(1), find_column(script, p.lexpos(1)), "@@" + p[3], p[4], p[6])

    def p_abstract_resource(p):
        r'resource : reference LBRACKET expression COLON attributes RBRACKET'
        if p[1].type != "Resource":
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        p[0] = Resource(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[3], p[5])

    def p_change_resource(p):
        r'resource : reference LBRACKET attributes RBRACKET'
        p[0] = Resource(p.lineno(1), find_column(script, p.lexpos(1)), p[1], None, p[3])

    def p_change_resource_collector(p):
        r'resource : resource_collector LBRACKET attributes RBRACKET'
        p[0] = Resource(p.lineno(1), find_column(script, p.lexpos(1)), p[1], None, p[3])

    def p_resource_default(p):
        r'resource : ID_TYPE LBRACKET attributes RBRACKET'
        p[0] = Resource(p.lineno(1), find_column(script, p.lexpos(1)), p[1], None, p[3])

    def p_resource_declaration(p):
        r'resource : DEFINE ID LPAREN parameters RPAREN LBRACKET block RBRACKET'
        p[0] = ResourceDeclaration(p.lineno(1), find_column(script, p.lexpos(1)), p[2], p[4], p[7])

    def p_resource_declaration_no_parameters(p):
        r'resource : DEFINE ID LBRACKET block RBRACKET'
        p[0] = ResourceDeclaration(p.lineno(1), find_column(script, p.lexpos(1)), p[2], [], p[4])

    def p_resource_collector(p):
        r'resource_collector : ID_TYPE LANGLEBRACKET rc_expression RANGLEBRACKET'
        p[0] = ResourceCollector(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[3])

    def p_resource_collector_empty(p):
        r'resource_collector : ID_TYPE LANGLEBRACKET RANGLEBRACKET'
        p[0] = ResourceCollector(p.lineno(1), find_column(script, p.lexpos(1)), p[1], None)

    def p_resource_collector_expression_equal(p):
        r'rc_expression : rc_expression CMP_EQUAL rc_expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_resource_collector_expression_not_equal(p):
        r'rc_expression : rc_expression CMP_NOT_EQUAL rc_expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_resource_collector_expression_and(p):
        r'rc_expression : rc_expression BOOL_AND rc_expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_resource_collector_expression_or(p):
        r'rc_expression : rc_expression BOOL_OR rc_expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_resource_collector_expression_paren(p):
        r'rc_expression : LPAREN rc_expression RPAREN'
        p[0] = p[2]

    def p_resource_collector_expression_value(p):
        r'rc_expression : rc_value'
        p[0] = p[1]

    def p_resource_collector_value(p):
        r'rc_value : value'
        p[0] = p[1]

    for k, v in statement_functions.items():
        exec(f"def p_resource_collector_value_{k}(p):\n\tr'rc_value : {v}'\n\tp[0] = p[1]")

    def p_parameters(p):
        r'parameters : parameter COMMA parameters'
        p[0] = [p[1]] + p[3]

    def p_parameters_single(p):
        r'parameters : parameter'
        p[0] = [p[1]]

    def p_parameters_empty(p):
        r'parameters : empty'
        p[0] = []

    def p_parameter(p):
        r'parameter : data_type ID EQUAL expression'
        p[0] = Parameter(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[2], p[4])

    def p_parameter_no_default(p):
        r'parameter : data_type ID'
        p[0] = Parameter(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[2], "")

    def p_parameter_only_name(p):
        r'parameter : ID'
        p[0] = Parameter(p.lineno(1), find_column(script, p.lexpos(1)), "", p[1], "")

    def p_parameter_default_without_type(p):
        r'parameter : ID EQUAL expression'
        p[0] = Parameter(p.lineno(1), find_column(script, p.lexpos(1)), "", p[1], p[3])

    def p_parameter_extra(p):
        r'parameter : ID ARITH_MUL ID EQUAL expression'
        p[0] = Parameter(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[2], p[4])

    def p_parameter_no_default_extra(p):
        r'parameter : ID ARITH_MUL ID'
        p[0] = Parameter(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[2], "")

    def p_parameter_only_name_extra(p):
        r'parameter : ARITH_MUL ID'
        p[0] = Parameter(p.lineno(1), find_column(script, p.lexpos(1)), "", p[1], "")

    def p_parameter_default_without_type_extra(p):
        r'parameter : ARITH_MUL ID EQUAL expression'
        p[0] = Parameter(p.lineno(1), find_column(script, p.lexpos(1)), "", p[1], p[3])

    def p_attributes(p):
        r'attributes : attribute COMMA attributes'
        p[0] = [p[1]] + p[3]

    def p_attributes_splat(p):
        r'attributes : attributes ARITH_MUL HASH_ROCKET expression'
        p[0] = [Attribute(p.lineno(2), find_column(script, p.lexpos(2)), p[2], p[4])]

    def p_attributes_splat_comma(p):
        r'attributes : attributes ARITH_MUL HASH_ROCKET expression COMMA'
        p[0] = [Attribute(p.lineno(2), find_column(script, p.lexpos(2)), p[2], p[4])]

    def p_attributes_single(p):
        r'attributes : attribute'
        p[0] = [p[1]]

    def p_attributes_empty(p):
        r'attributes : empty'
        p[0] = []

    def p_attribute(p):
        r'attribute : attributekey HASH_ROCKET expression'
        p[0] = Attribute(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[3])

    def p_attributekey(p):
        r'attributekey : ID'
        p[0] = p[1]
        p.set_lineno(0, p.lineno(1))

    for k, v in statement_functions.items():
        exec(f"def p_attributekey_{k}(p):\n\tr'attributekey : {v}'\n\tp[0] = p[1]\n\tp.set_lineno(0, p.lineno(1))")

    def p_array(p):
        r'array : LPARENR expressionlist RPARENR'
        p[0] = p[2]

    def p_hash(p):
        r'hash : LBRACKET keyvalue_pairs RBRACKET'
        res = {}
        for kv in p[2]:
            res[kv[0]] = kv[1]
        p[0] = res

    def p_keyvalue_pairs(p):
        r'keyvalue_pairs : keyvalue COMMA keyvalue_pairs'
        p[0] = [p[1]] + p[3]

    def p_keyvalue_pairs_single(p):
        r'keyvalue_pairs : keyvalue'
        p[0] = [p[1]]

    def p_keyvalue_pairs_empty(p):
        r'keyvalue_pairs : empty'
        p[0] = []

    def p_keyvalue(p):
        r'keyvalue : expression HASH_ROCKET expression'
        p[0] = (p[1], p[3])

    def p_expressionlist(p):
        r'expressionlist : expressionvalue COMMA expressionlist'
        p[0] = [p[1]] + p[3]

    def p_expressionlist_single(p):
        r'expressionlist : expressionvalue'
        p[0] = [p[1]]

    def p_expressionlist_empty(p):
        r'expressionlist : empty'
        p[0] = []

    def p_nonempty_expressionlist(p):
        r'nonempty_expressionlist : expressionvalue COMMA nonempty_expressionlist'
        p[0] = [p[1]] + p[3]

    def p_nonempty_expressionlist_single(p):
        r'nonempty_expressionlist : expressionvalue'
        p[0] = [p[1]]

    def p_expressionvalue(p):
        r'expressionvalue : expression'
        p[0] = p[1]

    def p_expressionvalue_type(p):
        r'expressionvalue : ID_TYPE'
        p[0] = p[1]

    ### Expressions ###
    def p_expression(p):
        'expression : value'
        p[0] = p[1]

    def p_expression_function_call(p):
        r'expression : function_call'
        p[0] = p[1]

    def p_expression_paren(p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression_assignment(p):
        r'expression : assignment'
        p[0] = p[1]

    def p_expression_access_section(p):
        r'expression : expression LPARENR INTEGER COMMA INTEGER RPARENR'
        p[0] = Operation((p[1], p[3], p[5]), p[2] + p[4] + p[6])

    ## Selector ##
    def p_expression_selector(p):
        r'expression : expression QUESTION_MARK hash'
        p[0] = Selector(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[3])

    ## Comparison ##
    def p_expression_equal(p):
        r'expression : expression CMP_EQUAL expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_not_equal(p):
        r'expression : expression CMP_NOT_EQUAL expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_less_than(p):
        r'expression : expression CMP_LESS_THAN expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_greater_than(p):
        r'expression : expression CMP_GREATER_THAN expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_less_than_or_equal(p):
        r'expression : expression CMP_LESS_THAN_OR_EQUAL expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_greater_than_or_equal(p):
        r'expression : expression CMP_GREATER_THAN_OR_EQUAL expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_regex_match(p):
        r'expression : expression CMP_REGEX_MATCH expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_regex_not_match(p):
        r'expression : expression CMP_REGEX_NOT_MATCH expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_in(p):
        r'expression : expression CMP_IN expression'
        p[0] = Operation((p[1], p[3]), p[2])

    ## Boolean
    def p_expression_and(p):
        r'expression : expression BOOL_AND expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_or(p):
        r'expression : expression BOOL_OR expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_not(p):
        r'expression : BOOL_NOT expression'
        p[0] = Operation((p[2],), p[1])

    ## Arithmetic
    def p_expression_negation(p):
        r'expression : ARITH_SUB expression %prec ARITH_MINUS'
        p[0] = Operation((p[2],), p[1])

    # It also works for array concatenation and hash merging
    def p_expression_addition(p):
        r'expression : expression ARITH_ADD expression'
        p[0] = Operation((p[1], p[3]), p[2])

    # It also works for array and hash removal
    def p_expression_subtraction(p):
        r'expression : expression ARITH_SUB expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_division(p):
        r'expression : expression ARITH_DIV expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_multiplication(p):
        r'expression : expression ARITH_MUL expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_modulo(p):
        r'expression : expression ARITH_MOD expression'
        p[0] = Operation((p[1], p[3]), p[2])

    # It also works for array append
    def p_expression_left_shift(p):
        r'expression : expression ARITH_LSHIFT expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_right_shift(p):
        r'expression : expression ARITH_RSHIFT expression'
        p[0] = Operation((p[1], p[3]), p[2])

    ## Array Operations
    def p_expression_splat(p):
        r'expression : ARITH_MUL expression %prec ARRAY_SPLAT'
        p[0] = Operation((p[2],), p[1])

    def p_expression_access(p):
        r'expression : expression LPARENR expressionlist RPARENR'
        p[0] = Operation((p[1], p[3]), p[2] + p[4])

    ## Reference
    def p_expression_reference(p):
        r'expression : reference'
        p[0] = p[1]

    def p_reference(p):
        r'reference : ID_TYPE LPARENR expressionlist RPARENR'
        p[0] = Reference(p.lineno(1), find_column(script, p.lexpos(1)),
                p[1], p[3])   

    # Function calls
    def p_function_call_prefix(p):
        r'function_call : ID LPAREN expressionlist RPAREN %prec NO_LAMBDA'
        p[0] = FunctionCall(p.lineno(1), find_column(script, p.lexpos(1)), 
                p[1], p[3], None)

    def p_function_call_prefix_lambda(p):
        r'function_call : ID LPAREN expressionlist RPAREN lambda %prec LAMBDA'
        p[0] = FunctionCall(p.lineno(1), find_column(script, p.lexpos(1)), 
                p[1], p[3], p[5])

    def p_function_call_chained(p):
        r'function_call : expression DOT ID %prec NO_LAMBDA'
        p[0] = FunctionCall(p.lineno(1), find_column(script, p.lexpos(1)), 
                p[3], [p[1]], None)

    def p_function_call_chained_args(p):
        r'function_call : expression DOT ID LPAREN expressionlist RPAREN %prec NO_LAMBDA'
        p[0] = FunctionCall(p.lineno(1), find_column(script, p.lexpos(1)), 
                p[3], [p[1]] + p[5], None) 

    def p_function_call_chained_lambda(p):
        r'function_call : expression DOT ID lambda %prec LAMBDA'
        p[0] = FunctionCall(p.lineno(1), find_column(script, p.lexpos(1)), 
                p[3], [p[1]], p[4])

    def p_function_call_chained_lambda_args(p):
        r'function_call : expression DOT ID LPAREN expressionlist RPAREN lambda %prec LAMBDA'
        p[0] = FunctionCall(p.lineno(1), find_column(script, p.lexpos(1)), 
                p[3], [p[1]] + p[5], p[7]) 

    def p_lambda(p):
        r'lambda : BAR parameters BAR LBRACKET block RBRACKET'
        p[0] = Lambda(p.lineno(1), find_column(script, p.lexpos(1)), p[2], p[5])

    def p_sensitive(p):
        r'function_call : SENSITIVE LPAREN STRING RPAREN'
        p[0] = FunctionCall(p.lineno(1), find_column(script, p.lexpos(1)), 
                p[1], (p[3],), None) 

    def p_sensitive_id(p):
        r'function_call : SENSITIVE DOT ID LPAREN STRING RPAREN'
        p[0] = FunctionCall(p.lineno(1), find_column(script, p.lexpos(1)), 
                p[1], (p[5],), None) 

    # Chaining arrows
    def p_chaining_left(p):
        'chaining : chaining_value CHAINING_LEFT chaining_value'
        p[0] = Chaining(p.lineno(1), find_column(script, p.lexpos(1)), 
                p[1], p[3], p[2])

    def p_chaining_right(p):
        'chaining : chaining_value CHAINING_RIGHT chaining_value'
        p[0] = Chaining(p.lineno(1), find_column(script, p.lexpos(1)), 
                p[1], p[3], p[2])

    def p_chaining_value(p):
        'chaining_value : chaining'
        p[0] = p[1]

    def p_chaining_value_array(p):
        'chaining_value : referencelist'
        if len(p[1]) == 1: 
            p[0] = p[1][0]
        else:
            p[0] = p[1]

    def p_chaining_value_resource(p):
        'chaining_value : resource'
        p[0] = p[1]

    def p_chaining_value_collector(p):
        'chaining_value : resource_collector'
        p[0] = p[1]

    def p_referencelist(p):
        r'referencelist : reference COMMA referencelist'
        p[0] = [p[1]] + p[3]

    def p_referencelist_single(p):
        r'referencelist : reference'
        p[0] = [p[1]]

    ### Statements ###
    # The statements are here because they need to be below the expressions
    # in order to have the correct behaviour when solving the reduce/reduce conflicts
    def p_statement_function(p):
        r'statement : function'
        p[0] = p[1]

    def p_statement_function_call(p):
        r'statement : function_call'
        p[0] = p[1]

    def p_statement_assignment(p):
        r'statement : assignment'
        p[0] = p[1]

    def p_statement_node(p):
        r'statement : node'
        p[0] = p[1]

    def p_statement_resource(p):
        r'statement : resource'
        p[0] = p[1]

    def p_statement_resource_collector(p):
        r'statement : resource_collector'
        p[0] = p[1]

    def p_statement_class(p):
        r'statement : class'
        p[0] = p[1]

    def p_statement_if(p):
        r'statement : if'
        p[0] = p[1]

    def p_statement_unless(p):
        r'statement : unless'
        p[0] = p[1]

    def p_statement_case(p):
        r'statement : case'
        p[0] = p[1]

    def p_statement_chaining(p):
        r'statement : chaining'
        p[0] = p[1]

    def p_statement_include(p):
        r'statement : INCLUDE nonempty_expressionlist'
        p[0] = Include(p.lineno(1), find_column(script, p.lexpos(1)), p[2])

    def p_statement_require(p):
        r'statement : REQUIRE nonempty_expressionlist'
        p[0] = Require(p.lineno(1), find_column(script, p.lexpos(1)), p[2])

    def p_statement_contain(p):
        r'statement : CONTAIN nonempty_expressionlist'
        p[0] = Contain(p.lineno(1), find_column(script, p.lexpos(1)), p[2])

    def p_statement_tag(p):
        r'statement : TAG nonempty_expressionlist'
        p[0] = Tag(p.lineno(1), find_column(script, p.lexpos(1)), p[2])

    def p_statement_debug(p):
        r'statement : DEBUG nonempty_expressionlist'
        p[0] = Debug(p.lineno(1), find_column(script, p.lexpos(1)), p[2])

    def p_statement_info(p):
        r'statement : INFO nonempty_expressionlist'
        p[0] = Debug(p.lineno(1), find_column(script, p.lexpos(1)), p[2])

    def p_statement_notice(p):
        r'statement : NOTICE nonempty_expressionlist'
        p[0] = Debug(p.lineno(1), find_column(script, p.lexpos(1)), p[2])

    def p_statement_warning(p):
        r'statement : WARNING nonempty_expressionlist'
        p[0] = Debug(p.lineno(1), find_column(script, p.lexpos(1)), p[2])

    def p_statement_err(p):
        r'statement : ERR nonempty_expressionlist'
        p[0] = Debug(p.lineno(1), find_column(script, p.lexpos(1)), p[2])

    def p_statement_fail(p):
        r'statement : FAIL nonempty_expressionlist'
        p[0] = Fail(p.lineno(1), find_column(script, p.lexpos(1)), p[2])

    def p_statement_realize(p):
        r'statement : REALIZE nonempty_expressionlist'
        p[0] = Realize(p.lineno(1), find_column(script, p.lexpos(1)), p[2])

    def p_statement_include_paren(p):
        r'statement : INCLUDE LPAREN expressionlist RPAREN'
        p[0] = Include(p.lineno(1), find_column(script, p.lexpos(1)), p[3])

    def p_statement_require_paren(p):
        r'statement : REQUIRE LPAREN expressionlist RPAREN'
        p[0] = Require(p.lineno(1), find_column(script, p.lexpos(1)), p[3])

    def p_statement_contain_paren(p):
        r'statement : CONTAIN LPAREN expressionlist RPAREN'
        p[0] = Contain(p.lineno(1), find_column(script, p.lexpos(1)), p[3])

    def p_statement_tag_paren(p):
        r'statement : TAG LPAREN expressionlist RPAREN'
        p[0] = Tag(p.lineno(1), find_column(script, p.lexpos(1)), p[3])

    def p_statement_debug_paren(p):
        r'statement : DEBUG LPAREN expressionlist RPAREN'
        p[0] = Debug(p.lineno(1), find_column(script, p.lexpos(1)), p[3])

    def p_statement_info_paren(p):
        r'statement : INFO LPAREN expressionlist RPAREN'
        p[0] = Debug(p.lineno(1), find_column(script, p.lexpos(1)), p[3])

    def p_statement_notice_paren(p):
        r'statement : NOTICE LPAREN expressionlist RPAREN'
        p[0] = Debug(p.lineno(1), find_column(script, p.lexpos(1)), p[3])

    def p_statement_warning_paren(p):
        r'statement : WARNING LPAREN expressionlist RPAREN'
        p[0] = Debug(p.lineno(1), find_column(script, p.lexpos(1)), p[3])

    def p_statement_err_paren(p):
        r'statement : ERR LPAREN expressionlist RPAREN'
        p[0] = Debug(p.lineno(1), find_column(script, p.lexpos(1)), p[3])

    def p_statement_fail_paren(p):
        r'statement : FAIL LPAREN expressionlist RPAREN'
        p[0] = Fail(p.lineno(1), find_column(script, p.lexpos(1)), p[3])

    def p_statement_realize_paren(p):
        r'statement : REALIZE LPAREN expressionlist RPAREN'
        p[0] = Realize(p.lineno(1), find_column(script, p.lexpos(1)), p[2])

    # Function declaration
    def p_function(p):
        r'function : FUNCTION ID LPAREN parameters RPAREN LBRACKET block RBRACKET'
        p[0] = Function(p.lineno(1), find_column(script, p.lexpos(1)), p[2],
                p[4], None, p[7])

    def p_function_return(p):
        r'function : FUNCTION ID LPAREN parameters RPAREN ARITH_RSHIFT data_type LBRACKET block RBRACKET '
        p[0] = Function(p.lineno(1), find_column(script, p.lexpos(1)), p[2],
                p[4], p[7], p[9])

    # Conditional statements
    def p_if(p):
        r'if : IF expression LBRACKET block RBRACKET'
        p[0] = If(p.lineno(1), find_column(script, p.lexpos(1)), p[2], p[4], None)

    def p_if_elsif(p):
        r'if : IF expression LBRACKET block RBRACKET elsif'
        p[0] = If(p.lineno(1), find_column(script, p.lexpos(1)), p[2], p[4], p[6])

    def p_elif(p):
        r'elsif : ELSIF expression LBRACKET block RBRACKET'
        p[0] = If(p.lineno(1), find_column(script, p.lexpos(1)), p[2], p[4], None)

    def p_elif_elif(p):
        r'elsif : ELSIF expression LBRACKET block RBRACKET elsif'
        p[0] = If(p.lineno(1), find_column(script, p.lexpos(1)), p[2], p[4], p[6])

    def p_else(p):
        r'elsif : ELSE LBRACKET block RBRACKET'
        p[0] = If(p.lineno(1), find_column(script, p.lexpos(1)), None, p[3], None)

    def p_unless(p):
        r'unless : UNLESS expression LBRACKET block RBRACKET'
        p[0] = Unless(p.lineno(1), find_column(script, p.lexpos(1)), p[2], p[4], None)

    def p_unless_else(p):
        r'unless : UNLESS expression LBRACKET block RBRACKET ELSE LBRACKET block RBRACKET'

        p[0] = Unless(p.lineno(1), find_column(script, p.lexpos(1)), p[2], p[4], 
            Unless(p.lineno(6), find_column(script, p.lexpos(6)), None, p[8], None))

    def p_case(p):
        r'case : CASE expression LBRACKET matches RBRACKET'
        p[0] = Case(p.lineno(1), find_column(script, p.lexpos(1)), p[2], p[4])

    def p_matches(p):
        r'matches : match matches'
        p[0] = [p[1]] + p[2]

    def p_matches_empty(p):
        r'matches : empty'
        p[0] = []
        
    def p_match(p):
        r'match : expressionlist COLON LBRACKET block RBRACKET'
        p[0] = Match(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[4])

    ### Data Type ###
    def p_data_type(p):
        r'data_type : ID_TYPE'
        p[0] = p[1]

    def p_data_type_reference(p):
        r'data_type : reference'
        p[0] = p[1]

    ### Values ###
    def p_value_hash(p):
        r'value : hash'
        p[0] = p[1]

    def p_value_array(p):
        r'value : array'
        p[0] = p[1]

    def p_value_string(p):
        r'value : STRING'
        p[0] = p[1]

    def p_value_false(p):
        r'value : FALSE'
        p[0] = False

    def p_value_true(p):
        r'value : TRUE'
        p[0] = True

    def p_value_integer(p):
        r'value : INTEGER'
        p[0] = int(p[1])

    def p_value_float(p):
        r'value : FLOAT'
        p[0] = float(p[1])

    def p_value_regex(p):
        r'value : REGEX'
        p[0] = Regex(p[1])

    def p_value_id(p):
        r'value : ID'
        p[0] = p[1]

    def p_value_type_id(p):
        r'value : ID_TYPE'
        p[0] = p[1]

    def p_value_undef(p):
        r'value : UNDEF'
        p[0] = None

    def p_value_default(p):
        r'value : DEFAULT'
        p[0] = p[1]

    def p_empty(p):
        r'empty : '
    
    def p_error(p):
        print(f'Syntax error at {p.value!r}')

    # Build the parser
    parser = yacc()
    return parser.parse(script), comments