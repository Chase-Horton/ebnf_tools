# Python EBNF Parser

A tool for parsing and validating EBNF files and generating random text following the grammar.

## Usage

```python
from ebnf_tools import Parser, RandomGenerator

#create a parser to parse the file
parser = Parser("./pascal.ebnf")

#build an abstract syntax tree and return a GrammarNode object representing the root of the tree
ast = parser.parse()

# get a list of undefined identifiers used in assignments (invalid usage)
undefined_symbols = ast.undefined()
if len(undefined_symbols) > 0:
   raise Exception("Invalid EBNF")

# Generating random text that meet a grammar rule
# assignment = identifier , ":=" , ( number | identifier | string ) ;
generator = RandomGenerator(ast)
for _ in range(5):
   print(generator.generate('assignment'))
# ER:=""
# QF8:=-244
# I8:=""
# M4I9:=UIX
# C:=-4


print(generator.generate('program'))
# PROGRAM T1V BEGIN
# SZM:="NEE";
# VC24:=21;
# N4HI:=8;
# END.
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
