#!/usr/bin/env python3

from tokenizer import Tokenizer
# from parser import Parser

# from tabatkins/css-parser originally 
# correct output from https://tabatkins.github.io/parse-css/example.html
tests = [
    (
        "foo { bar: baz; }",
        "IDENT(foo) WS OPEN-CURLY WS IDENT(bar) COLON WS IDENT(baz) SEMICOLON WS CLOSE-CURLY EOF"
    ),
    (
        "foo { bar: rgb(255, 0, 127); }",
        "IDENT(foo) WS OPEN-CURLY WS IDENT(bar) COLON WS FUNCTION(rgb) INT(255) COMMA WS INT(0) COMMA WS INT(127) CLOSE-PAREN SEMICOLON WS CLOSE-CURLY EOF"
    ),
    (
        "#foo {}",
        "HASH(foo) WS OPEN-CURLY CLOSE-CURLY EOF"
    ),
    (
        "@media{ }",
        "AT(media) OPEN-CURLY WS CLOSE-CURLY EOF",
    ),
    (
        """p > a {
            color: blue;
            text-decoration: underline;
        }""",
        "IDENT(p) WS DELIM(>) WS IDENT(a) WS OPEN-CURLY WS IDENT(color) COLON WS IDENT(blue) SEMICOLON WS IDENT(text-decoration) COLON WS IDENT(underline) SEMICOLON WS CLOSE-CURLY EOF"
    ),
    (
        """@import "my-styles.css";""",
        "AT(import) WS STRING(my-styles.css) SEMICOLON EOF"
    ),
    (
        """@page :left {
            margin-left: 4cm;
            margin-right: 3cm;
        }""",
        "AT(page) WS COLON IDENT(left) WS OPEN-CURLY WS IDENT(margin-left) COLON WS DIM(4, cm) SEMICOLON WS IDENT(margin-right) COLON WS DIM(3, cm) SEMICOLON WS CLOSE-CURLY EOF"
    ),
    (
        """body { font-size: 10pt; }""",
        "IDENT(body) WS OPEN-CURLY WS IDENT(font-size) COLON WS DIM(10, pt) SEMICOLON WS CLOSE-CURLY EOF"
    ),
    (
        """@media print {
            body { font-size: 10pt }
        }""",
        "AT(media) WS IDENT(print) WS OPEN-CURLY WS IDENT(body) WS OPEN-CURLY WS IDENT(font-size) COLON WS DIM(10, pt) WS CLOSE-CURLY WS CLOSE-CURLY EOF"
    ),
    (
        """body {
            font-family: 'Helvetica Neue';
        }""",
        "IDENT(body) WS OPEN-CURLY WS IDENT(font-family) COLON WS STRING(Helvetica Neue) SEMICOLON WS CLOSE-CURLY EOF",
    ),
    (
        """/* a comment */""",
        "EOF"
    ),
    (
        """p.lead {
            margin: 1em 10px +5px -10px;
            padding: .5em;
            line-height: 1.5;
        }""",
        "IDENT(p) DELIM(.) IDENT(lead) WS OPEN-CURLY WS IDENT(margin) COLON WS DIM(1, em) WS DIM(10, px) WS DIM(+5, px) WS DIM(-10, px) SEMICOLON WS IDENT(padding) COLON WS DIM(0.5, em) SEMICOLON WS IDENT(line-height) COLON WS NUMBER(1.5) SEMICOLON WS CLOSE-CURLY EOF"
    ),
    # extras
    (
        "div p *[href] {}",
        "IDENT(div) WS IDENT(p) WS DELIM(*) OPEN-SQUARE IDENT(href) CLOSE-SQUARE WS OPEN-CURLY CLOSE-CURLY EOF"
    ),
    (
        "a + b {}",
        "IDENT(a) WS DELIM(+) WS IDENT(b) WS OPEN-CURLY CLOSE-CURLY EOF"
    ),
]


t = Tokenizer()

for css, tokenization in tests:
    tokens = []
    for token in t.tokenize(css):
        if len(token) == 3:
            tokens.append(f"{token[0]}({token[1]}, {token[2]})")
        elif len(token) == 2:
            tokens.append(f"{token[0]}({token[1]})")
        else:
            tokens.append(token[0])
    if " ".join(tokens) != tokenization:
        print(css)
        print("FAIL")
        print("GOT:     ", " ".join(tokens))
        print("EXPECTED:", tokenization)
