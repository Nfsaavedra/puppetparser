from ast import keyword
from ply.lex import lex
from ply.yacc import yacc
import re
from puppetparser.model import Attribute, Resource

def parser_yacc(script):
    tokens = (
        # Keywords
        'AND', 
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
        'OR',
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
        # SYNTAX SUGAR
        'LBRACKET',
        'RBRACKET',
        'COLON',
        'HASH_ROCKET',
        'COMMA',
        # Identifiers
        'ID',
    )

    keywords = {
        'and': 'AND', 
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
        'in': 'IN',
        'inherits': 'INHERITS',
        'node': 'NODE',
        'or': 'OR',
        'private': 'PRIVATE',
        'produces': 'PRODUCES',
        'regexp': 'REGEXP',
        'site': 'SITE',
        'true': 'TRUE',
        'type': 'TYPE',
        'undef': 'UNDEF',
        'unit': 'UNIT',
        'unless': 'UNLESS',
    }

    states = (
    )

    # Other
    t_LBRACKET = r'\{'
    t_RBRACKET = r'\}'
    t_COLON = r'\:'
    t_HASH_ROCKET = r'=>'
    t_COMMA = r','
    t_INTEGER = r'-?(0|[1-9]\d*)'
    t_FLOAT = r'(-?(0|[1-9]\d*)(\.\d+)?)'

    # Identifiers
    t_ignore_ANY = r'[\t\ \n]'

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

    def t_sci_not_FLOAT(t):
        r'(-?(0|[1-9]\d*)(\.\d+)?(e-?(0|[1-9]\d*))?)'
        t.type = "FLOAT"
        return t

    def t_ID(t):
        r'[A-Za-z][a-z0-9\.\_\-\:]*'
        t.type = keywords.get(t.value,'ID')
        return t

    def t_STRING(t):
        r"(\'([^\\\n]|(\\.))*?\')|(\"([^\\\n]|(\\.))*?\")"
        t.value = t.value[1:-1]
        return t

    def t_ANY_error(t):
        print(f'Illegal character {t.value[0]!r}.')
        t.lexer.skip(1)

    lexer = lex()
    # Give the lexer some input
    lexer.input(script)

    #while True:
    #    tok = lexer.token()
    #    if not tok: 
    #        break      # No more input
    #    print(tok)

    def p_resource(p):
        r'resource : ID LBRACKET STRING COLON attributes RBRACKET'
        p[0] = Resource(0, 0, p[1], p[3], p[5])

    def p_attributes(p):
        r'attributes : attribute attributes'
        p[0] = [p[1]] + p[2]

    def p_attributes_empty(p):
        r'attributes : empty'
        p[0] = []

    def p_attribute(p):
        r'attribute : ID HASH_ROCKET value COMMA'
        if not re.match(r"^[a-z]+$", p[1]):
            print(f'Syntax error!') #FIXME
        p[0] = Attribute(0, 0, p[1], p[3])

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

    def p_value_id(p):
        r'value : ID'
        if not re.match(r"^[a-z][A-Za-z0-9\-\_]*$", p[1]):
            print(f'Syntax error!') #FIXME
        p[0] = p[1]

    def p_empty(p):
        r'empty : '
    
    def p_error(p):
        print(f'Syntax error at {p.value!r}')

    # Build the parser
    parser = yacc()
    return parser.parse(script)