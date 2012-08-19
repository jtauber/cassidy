#!/usr/bin/env python

from tokenizer import Tokenizer
from parser import Parser

# from tabatkins/css-parser
tests = [
    "foo { bar: baz; }",
    "foo { bar: rgb(255, 0, 127); }",
    "#foo {}",
    "@media{ }",
    """
    p > a {
        color: blue;
        text-decoration: underline;
    }
    """,
    """@import "my-styles.css";""",
    """
    @page :left {
        margin-left: 4cm;
        margin-right: 3cm;
    }
    """,
    """
    @media print {
        body { font-size: 10pt }
    }
    """,
    """
    body {
        font-family: 'Helvetica Neue';
    }
    """,
    """
    /* a comment */
    """,
    """
    p.lead {
        margin: 1em 10px +5px -10px;
        padding: .5em;
        line-height: 1.5;
    }
    """,
]

# extras
tests += [
    "div p *[href] {}",
    "a + b {}",
]

for test in tests:
    print
    print test
    t = Tokenizer(test)
    tokens = list(t.tokenize())
    print tokens
    p = Parser(tokens)
    p.parse()
    p.open_rule_stack[0].pretty_print()
