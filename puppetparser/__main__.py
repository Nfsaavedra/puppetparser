from puppetparser.parser import parser_yacc

with open("test.pp", "r") as f:
    print(parser_yacc(f.read()))