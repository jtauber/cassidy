from tokenizer import tokenize


TOP_LEVEL_MODE = 1
AT_RULE_MODE = 2
RULE_MODE = 3
SELECTOR_MODE = 4
DECLARATION_MODE = 5
AFTER_DECLARATION_NAME_MODE = 6
DECLARATION_VALUE_MODE = 7
DECLARATION_END_MODE = 8
NEXT_BLOCK_ERROR_MODE = 9
NEXT_DECLARATION_ERROR_MODE = 10


class style_rule:
    pass


def parse(tokens):
    index = 0
    mode = TOP_LEVEL_MODE
    open_rule_stack = []
    
    while index < len(tokens):
        if mode == TOP_LEVEL_MODE:
            token = tokens[index]
            index += 1
            if token[0] == "cdo" or token[0] == "cdc" or token[0] == "whitespace":
                pass
            elif token[0] == "at_keyword":
                rule = at_rule(name=token[1])
                open_rule_stack.append(rule)
                mode = AT_RULE_MODE
            elif token[0] == "{":
                # @@@ parse error
                pass  # @@@ TODO
            elif token[0] == "EOF":
                pass  # @@@ TODO
            else:
                rule = style_rule()
                open_rule_stack.append(rule)
                mode = SELECTOR_MODE
                index -= 1
        else:
            print "UNKNOWN MODE", mode
            break


if __name__ == "__main__":
    print parse(list(tokenize("""
    p > a {
        color: blue;
        text-decoration: underline;
    }
    """)))
