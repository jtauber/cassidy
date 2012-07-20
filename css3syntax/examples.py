#!/usr/bin/env python

from tokenizer import tokenize
from parser import Parser

# from tabatkins/css-parser
tests = [
    "foo { bar: baz; }",
    "foo { bar: rgb(255, 0, 127); }",
    "#foo {}",
    "@media{ }",
]

for test in tests:
    print
    print test
    tokens = list(tokenize(test))
    print tokens
    p = Parser(tokens)
    p.parse()
    p.open_rule_stack[0].pretty_print()
