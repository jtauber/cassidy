def is_digit(ch):
    return "0" <= ch <= "9"


def is_hex_digit(ch):
    return is_digit(ch) or "A" <= ch <= "F" or "a" <= ch <= "f"


def is_uppercase_letter(ch):
    return "A" <= ch <= "Z"


def is_lowercase_letter(ch):
    return "a" <= ch <= "z"


def is_letter(ch):
    return is_uppercase_letter(ch) or is_lowercase_letter(ch)


def is_non_ascii_character(ch):
    return ch >= "\u00A0"


def is_name_start_character(ch):
    return is_letter(ch) or is_non_ascii_character(ch) or ch == "_"
    # @@@ *any* non-ascii can start a name?


def is_name_character(ch):
    return is_name_start_character(ch) or is_digit(ch) or ch == "-"


def is_non_printable_character(ch):
    return "\u0000" <= ch <= "\u0008" or "\u000E" <= ch <= "\u001F" or "\u007F" <= ch <= "\009F"


def is_newline(ch):
    return ch == "\n" or ch == "\f"
    # carriage return removed in preprocessing


def is_whitespace(ch):
    return is_newline(ch) or ch == "\t" or ch == " "


DATA_STATE = 1
DOUBLE_QUOTE_STRING_STATE = 2
SINGLE_QUOTE_STRING_STATE = 3
HASH_STATE = 4
HASH_REST_STATE = 5
COMMENT_STATE = 6
AT_KEYWORD_STATE = 7
AT_KEYWORD_REST_STATE = 8
IDENTIFIER_STATE = 9
IDENTIFIER_REST_STATE = 10
TRANSFORM_FUNCTION_WHITESPACE_STATE = 11
NUMBER_STATE = 12
NUMBER_RESET_STATE = 13
NUMBER_FRACTION_STATE = 14
DIMENSION_STATE = 15
SCI_NOTATION_STATE = 16
URL_STATE = 17
URL_DOUBLE_QUOTE_STATE = 18
URL_SINGLE_QUOTE_STATE = 19
URL_END_STATE = 20
URL_UNQUOTED_STATE = 21
BAD_URL_STATE = 22
UNICODE_RANGE_STATE = 23


def tokenize(s):
    index = 0
    state = DATA_STATE
    tmp_string = None
    transform_function_whitespace = False
    
    while index < len(s):
        if state == DATA_STATE:
            ch = s[index]
            index += 1
            if is_whitespace(ch):
                while index < len(s) and is_whitespace(s[index]):
                    index += 1
                yield ("whitespace",)
            elif ch == "\"":
                state = DOUBLE_QUOTE_STRING_STATE
            elif ch == "#":
                state = HASH_STATE
            elif ch == "'":
                state = SINGLE_QUOTE_STRING_STATE
            elif ch == "(":
                yield ("(",)
            elif ch == ")":
                yield (")",)
            elif ch == "+":
                if is_digit(s[index]) or s[index] == "." and is_digit(s[index + 1]):
                    state = NUMBER_STATE
                    index -= 1
            elif ch == "-":
                if s[index:index + 2] == "->":
                    yield ("CDC",)
                    index += 2
                elif is_digit(s[index]) or s[index] == "." and is_digit(s[index + 1]):
                    state = NUMBER_STATE
                    index -= 1
                elif is_name_start_character(s[index]):
                    state = IDENTIFIER_STATE
                    index -= 1
                else:
                    yield ("delim", "-")
            elif ch == ".":
                if is_digit(s[index]):
                    state = NUMBER_STATE
                    index -= 1
                else:
                    yield ("delim", ".")
            elif ch == "/":
                if s[index] == "*":
                    index += 1
                    state = COMMENT_STATE
                else:
                    yield ("delim", "/")
            elif ch == ":":
                yield ("colon",)
            elif ch == ";":
                yield (";",)
            elif ch == "<":
                if s[index:index + 3] == "!--":
                    index += 3
                    yield ("cdo",)
                else:
                    yield ("delim", "<")
            elif ch == "@":
                state = AT_KEYWORD_STATE
            elif ch == "[":
                yield ("[",)
            elif ch == "\\":
                if index > len(s) or is_newline(s[index]):
                    # @@@ parse error
                    yield ("delim", "\\")
                else:
                    state = IDENTIFIER_STATE
                    index -= 1
            elif ch == "]":
                yield ("]",)
            elif ch == "{":
                yield ("{",)
            elif ch == "}":
                yield ("}",)
            elif is_digit(ch):
                state = NUMBER_STATE
                index -= 1
            elif ch == "U" or ch == "u":
                if s[index] == "+" and is_hex_digit(s[index + 1]):
                    index += 1
                    state = UNICODE_RANGE_STATE
                elif s[index:index + 3].lower() == "rl(":
                    index += 3
                    state = URL_STATE
                else:
                    state = IDENTIFIER_STATE
                    index -= 1
            elif is_name_start_character(ch):
                state = IDENTIFIER_STATE
                index -= 1
            elif index > len(s):
                yield ("EOF",)
            else:
                yield ("delim", ch)
        elif state == DOUBLE_QUOTE_STRING_STATE:
            if tmp_string is None:
                tmp_string = ""
            ch = s[index]
            index += 1
            if ch == "\"":
                yield ("string", tmp_string)
                tmp_string = None
                state = DATA_STATE
            elif index > len(s):
                yield ("EOF", )
            elif is_newline(ch):
                # @@@ parse error
                yield ("bad-string",)
                state = DATA_STATE
                index -= 1
            elif ch == "\\":
                if index > len(s):
                    # @@@ parse error
                    yield ("bad-string",)
                    state = DATA_STATE
                elif is_newline(s[index]):
                    index += 1
                else:
                    # consume an escaped character
                    pass  # @@@ TODO
            else:
                tmp_string += ch
        elif state == SINGLE_QUOTE_STRING_STATE:
            if tmp_string is None:
                tmp_string = ""
            ch = s[index]
            index += 1
            if ch == "'":
                yield ("string", tmp_string)
                tmp_string = None
                state = DATA_STATE
            elif index > len(s):
                yield ("EOF", )
            elif is_newline(ch):
                # @@@ parse error
                yield ("bad-string",)
                state = DATA_STATE
                index -= 1
            elif ch == "\\":
                if index > len(s):
                    # @@@ parse error
                    yield ("bad-string",)
                    state = DATA_STATE
                elif is_newline(s[index]):
                    index += 1
                else:
                    # consume an escaped character
                    pass  # @@@ TODO
            else:
                tmp_string += ch
        elif state == HASH_STATE:
            ch = s[index]
            index += 1
            if is_name_character(ch):
                tmp_hash = ch
                state = HASH_REST_STATE
            elif ch == "\\":
                if index > len(s) or is_newline(s[index]):
                    yield ("delim", "#")
                    state = DATA_STATE
                    index -= 1
                else:
                    # consume an escaped character
                    pass  # @@@ TODO
            else:
                yield ("delim", "#")
                state = DATA_STATE
                index -= 1
        elif state == HASH_REST_STATE:
            ch = s[index]
            index += 1
            if is_name_character(ch):
                tmp_hash += ch
            elif ch == "\\":
                if index > len(s) or is_newline(s[index]):
                    yield ("hash", tmp_hash)
                    state = DATA_STATE
                    index -= 1
                else:
                    # consume an escaped character
                    pass  # @@@ TODO
            else:
                yield ("hash", tmp_hash)
                state = DATA_STATE
                index -= 1
        elif state == COMMENT_STATE:
            ch = s[index]
            index += 1
            if ch == "*":
                if s[index] == "/":
                    index += 1
                    state = DATA_STATE
                else:
                    pass
            elif index > len(s):
                # @@@ parse error
                state = DATA_STATE
                index -= 1
            else:
                pass
        elif state == AT_KEYWORD_STATE:
            ch = s[index]
            index += 1
            if ch == "-":
                if is_name_start_character(s[index]):
                    tmp_at_keyword = "-" + s[index]
                    index += 1
                    state = AT_KEYWORD_REST_STATE
                else:
                    yield ("delim", "@")
                    state = DATA_STATE
                    index -= 1
            elif is_name_start_character(ch):
                tmp_at_keyword = ch
                state = AT_KEYWORD_REST_STATE
            elif ch == "\\":
                if index > len(s) or is_newline(s[index]):
                    yield ("delim", "@")
                    state = DATA_STATE
                    index -= 1
                else:
                    # consume an escaped character
                    pass  # @@@ TODO
            else:
                yield ("delim", "@")
                state = DATA_STATE
                index -= 1
        # AT_KEYWORD_REST_STATE
        elif state == IDENTIFIER_STATE:
            ch = s[index]
            index += 1
            if ch == "-":
                if is_name_start_character(s[index]):
                    tmp_identifier = "-"
                    state = IDENTIFIER_REST_STATE
                else:
                    state = DATA_STATE
                    index -= 1
            elif is_name_start_character(ch):
                tmp_identifier = ch
                state = IDENTIFIER_REST_STATE
            elif ch == "\\":
                if index > len(s) or is_newline(s[index]):
                    state = DATA_STATE
                    index -= 1
                else:
                    # consume an escaped character
                    pass  # @@@ TODO
            else:
                state = DATA_STATE
                index -= 1
        elif state == IDENTIFIER_REST_STATE:
            ch = s[index]
            index += 1
            if is_name_character(ch):
                tmp_identifier += ch
            elif ch == "\\":
                if index > len(s) or is_newline(s[index]):
                    state = DATA_STATE
                    index -= 1
                else:
                    # consume an escaped character
                    pass  # @@@ TODO
            elif ch == "(":
                yield ("function", tmp_identifier)
                state = DATA_STATE
            elif is_whitespace(ch):
                if transform_function_whitespace:
                    state = TRANSFORM_FUNCTION_WHITESPACE_STATE
                else:
                    yield ("identifier", tmp_identifier)
                    state = DATA_STATE
                    index -= 1
            else:
                yield ("identifier", tmp_identifier)
                state = DATA_STATE
                index -= 1
        else:
            print "UNKNOWN STATE", state
            raise StopIteration


if __name__ == "__main__":
    for token in tokenize("""
    p > a {
        color: blue;
        text-decoration: underline;
    }
    """):
        print token
