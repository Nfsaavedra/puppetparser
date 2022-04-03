from puppetparser.parser import parse

with open("test.pp", "r") as f:
    print(parse(f.read()))