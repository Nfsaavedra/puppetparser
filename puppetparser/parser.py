from ply.lex import lex
from ply.yacc import yacc
import re
from puppetparser.model import Assignment, Attribute, Comment, Node, Operation, Parameter, PuppetClass, Regex, Resource

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
        'ENVIRONMENT',
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
        # SYNTAX SUGAR
        'LBRACKET',
        'RBRACKET',
        'LPAREN',
        'RPAREN',
        'LPARENR',
        'RPARENR',
        'EQUAL',
        'COLON',
        'HASH_ROCKET',
        'COMMA',
        # Identifiers
        'ID',
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
        'ARITH_RSHIFT'
    )

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
        'environment': 'ENVIRONMENT',
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
    t_HASH_ROCKET = r'=>'
    t_COLON = r'\:'
    t_COMMA = r','
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
        r'[A-Za-z\$][a-z0-9\.\_\-\:]*'
        t.type = keywords.get(t.value,'ID')
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
        ('left', 'EQUAL'),
        ('left', 'BOOL_OR'),
        ('left', 'BOOL_AND'),
        ('nonassoc', 'CMP_LESS_THAN', 'CMP_GREATER_THAN', 'CMP_LESS_THAN_OR_EQUAL', 'CMP_GREATER_THAN_OR_EQUAL'),
        ('nonassoc', 'CMP_EQUAL', 'CMP_NOT_EQUAL'),
        ('left', 'ARITH_LSHIFT', 'ARITH_RSHIFT'),
        ('left', 'ARITH_ADD', 'ARITH_SUB'),
        ('left', 'ARITH_MUL', 'ARITH_DIV', 'ARITH_MOD'),
        ('left', 'CMP_REGEX_MATCH', 'CMP_REGEX_NOT_MATCH'),
        ('left', 'CMP_IN'),
        ('right', 'ARITH_MINUS'),
        ('right', 'BOOL_NOT'),
    )

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

    def p_class_header_inherits(p):
        r'class_header : ID LPAREN parameters RPAREN INHERITS ID'
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[6]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        p[0] = (p[1], p[3], p[6])

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

    def p_block_empty(p):
        r'block : empty'
        p[0] = []

    def p_statement_assignment(p):
        r'statement : assignment'
        p[0] = p[1]

    def p_statement_node(p):
        r'statement : node'
        p[0] = p[1]

    def p_statement_resource(p):
        r'statement : resource'
        p[0] = p[1]

    def p_statement_class(p):
        r'statement : class'
        p[0] = p[1]

    def p_resource(p):
        r'resource : ID LBRACKET STRING COLON attributes RBRACKET'
        if not re.match(r"([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*", p[1]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        p[0] = Resource(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[3], p[5])

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
        r'parameter : ID ID EQUAL expression'
        p[0] = Parameter(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[2], p[4])

    def p_parameter_no_default(p):
        r'parameter : ID ID'
        p[0] = Parameter(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[2], "")

    def p_parameter_only_name(p):
        r'parameter : ID'
        p[0] = Parameter(p.lineno(1), find_column(script, p.lexpos(1)), "", p[1], "")

    def p_parameter_default_without_type(p):
        r'parameter : ID EQUAL expression'
        p[0] = Parameter(p.lineno(1), find_column(script, p.lexpos(1)), "", p[1], p[3])

    def p_attributes(p):
        r'attributes : attribute COMMA attributes'
        p[0] = [p[1]] + p[3]

    def p_attributes_single(p):
        r'attributes : attribute'
        p[0] = [p[1]]

    def p_attributes_empty(p):
        r'attributes : empty'
        p[0] = []

    def p_attribute(p):
        r'attribute : ID HASH_ROCKET expression'
        if not re.match(r"^[a-z]+$", p[1]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        p[0] = Attribute(p.lineno(1), find_column(script, p.lexpos(1)), p[1], p[3])

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
        r'expressionlist : expression COMMA expressionlist'
        p[0] = [p[1]] + p[3]

    def p_valuelist_single(p):
        r'expressionlist : expression'
        p[0] = [p[1]]

    def p_expressionlist_empty(p):
        r'expressionlist : empty'
        p[0] = []

    ### Expressions ###
    def p_expression(p):
        'expression : value'
        p[0] = p[1]

    def p_expression_paren(p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression_assignment(p):
        r'expression : assignment'
        p[0] = p[1]

    def p_expression_access(p):
        r'expression : expression LPARENR expression RPARENR'
        p[0] = Operation((p[1], p[3]), p[2] + p[4])

    def p_expression_access_section(p):
        r'expression : expression LPARENR INTEGER COMMA INTEGER RPARENR'
        p[0] = Operation((p[1], p[3], p[5]), p[2] + p[4] + p[6])

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

    def p_expression_addition(p):
        r'expression : expression ARITH_ADD expression'
        p[0] = Operation((p[1], p[3]), p[2])

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

    def p_expression_left_shift(p):
        r'expression : expression ARITH_LSHIFT expression'
        p[0] = Operation((p[1], p[3]), p[2])

    def p_expression_right_shift(p):
        r'expression : expression ARITH_RSHIFT expression'
        p[0] = Operation((p[1], p[3]), p[2])

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
        if not re.match(r"^[a-z][A-Za-z0-9\-\_]*$", p[1]) and \
                not re.match(r"^\$[a-z0-9_][a-zA-Z0-9_]*$", p[1]) and \
                not re.match(r"^\$([a-z][a-z0-9_]*)?(::[a-z][a-z0-9_]*)*::[a-z0-9_][a-zA-Z0-9_]*$", p[1]):
            print(f'Syntax error on line {p.lineno(1)}: {p.value}.')
        p[0] = p[1]

    def p_empty(p):
        r'empty : '
    
    def p_error(p):
        print(f'Syntax error at {p.value!r}')

    # Build the parser
    parser = yacc()
    return parser.parse(script), comments