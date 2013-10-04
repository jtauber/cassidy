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
    return ch >= "\xA0"


def is_name_start_character(ch):
    return is_letter(ch) or is_non_ascii_character(ch) or ch == "_"
    # @@@ *any* non-ascii can start a name?


def is_name_character(ch):
    return is_name_start_character(ch) or is_digit(ch) or ch == "-"


def is_non_printable_character(ch):
    return "\x00" <= ch <= "\x08" or "\x0E" <= ch <= "\x1F" or "\x7F" <= ch <= "\x9F"


def is_newline(ch):
    return ch == "\n" or ch == "\f"
    # carriage return removed in preprocessing


def is_whitespace(ch):
    return is_newline(ch) or ch == "\t" or ch == " "


MAXIMUM_ALLOWED_CODEPOINT = 0x10FFFF

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
NUMBER_REST_STATE = 13
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


class Tokenizer:
    
    def __init__(self, s):
        self.index = 0
        self.s = s
        self.state = DATA_STATE
        self.tmp_string = None
        self.supports_scientific_notation = False
        self.transform_function_whitespace = False
    
    def tokenize(self):
        while self.index < len(self.s):
            if self.state == DATA_STATE:
                for token in self.data_state():
                    yield token
            elif self.state == DOUBLE_QUOTE_STRING_STATE:
                for token in self.double_quote_string_state():
                    yield token
            elif self.state == SINGLE_QUOTE_STRING_STATE:
                for token in self.single_quote_string_state():
                    yield token
            elif self.state == HASH_STATE:
                for token in self.hash_state():
                    yield token
            elif self.state == HASH_REST_STATE:
                for token in self.hash_rest_state():
                    yield token
            elif self.state == COMMENT_STATE:
                for token in self.comment_state():
                    yield token
            elif self.state == AT_KEYWORD_STATE:
                for token in self.at_keyword_state():
                    yield token
            elif self.state == AT_KEYWORD_REST_STATE:
                for token in self.at_keyword_rest_state():
                    yield token
            elif self.state == IDENTIFIER_STATE:
                for token in self.identifier_state():
                    yield token
            elif self.state == IDENTIFIER_REST_STATE:
                for token in self.identifier_rest_state():
                    yield token
            # TRANSFORM_FUNCTION_WHITESPACE_STATE
            elif self.state == NUMBER_STATE:
                for token in self.number_state():
                    yield token
            elif self.state == NUMBER_REST_STATE:
                for token in self.number_rest_state():
                    yield token
            elif self.state == NUMBER_FRACTION_STATE:
                for token in self.number_fraction_state():
                    yield token
            elif self.state == DIMENSION_STATE:
                for token in self.dimension_state():
                    yield token
            else:
                raise Exception("UNKNOWN STATE %s" % self.state)
    
    def consume_next_input_character(self):
        ch = self.s[self.index]
        self.index += 1
        return ch
    
    def consume_whitespace(self):
        while self.index < len(self.s) and is_whitespace(self.s[self.index]):
            self.index += 1
    
    def consume_escaped_character(self):
        ch = self.consume_next_input_character()
        if is_hex_digit(ch):
            digits = ch
            while len(digits) <= 6:
                ch = self.consume_next_input_character()
                if is_hex_digit(ch):
                    digits += ch
                elif is_whitespace(ch):
                    pass
                else:
                    self.reconsume_input_character()
                    break
            code_point = int(digits, 16)
            if code_point > MAXIMUM_ALLOWED_CODEPOINT:
                return u"\uFFFD"
            else:
                return unichr(code_point)
        else:
            return ch
    
    def next_input_character(self, size=1):
        return self.s[self.index:self.index + size]
    
    def reconsume_input_character(self):
        self.index -= 1
    
    def data_state(self):
        ch = self.consume_next_input_character()
        if is_whitespace(ch):
            self.consume_whitespace()
            yield ("whitespace",)
        elif ch == "\"":
            self.state = DOUBLE_QUOTE_STRING_STATE
        elif ch == "#":
            self.state = HASH_STATE
        elif ch == "'":
            self.state = SINGLE_QUOTE_STRING_STATE
        elif ch == "(":
            yield ("(",)
        elif ch == ")":
            yield (")",)
        elif ch == "+":
            chs = self.next_input_character(2)
            if is_digit(chs[0]) or (chs[0] == "." and is_digit(chs[1])):
                self.state = NUMBER_STATE
                self.reconsume_input_character()
            else:
                yield ("delim", "+")
        elif ch == "-":
            chs = self.next_input_character(2)
            if chs == "->":
                yield ("cdc",)
                self.index += 2
            elif is_digit(chs[0]) or (chs[0] == "." and is_digit(chs[1])):
                self.state = NUMBER_STATE
                self.reconsume_input_character()
            elif is_name_start_character(chs[0]):
                self.state = IDENTIFIER_STATE
                self.reconsume_input_character()
            else:
                yield ("delim", "-")
        elif ch == ".":
            if is_digit(self.next_input_character()):
                self.state = NUMBER_STATE
                self.reconsume_input_character()
            else:
                yield ("delim", ".")
        elif ch == "/":
            if self.next_input_character() == "*":
                self.index += 1
                self.state = COMMENT_STATE
            else:
                yield ("delim", "/")
        elif ch == ":":
            yield ("colon",)
        elif ch == ";":
            yield ("semicolon",)
        elif ch == "<":
            chs = self.next_input_character(3)
            if chs == "!--":
                self.index += 3
                yield ("cdo",)
            else:
                yield ("delim", "<")
        elif ch == "@":
            self.state = AT_KEYWORD_STATE
        elif ch == "[":
            yield ("[",)
        elif ch == "\\":
            if self.index > len(self.s) or is_newline(self.next_input_character()):
                # @@@ parse error
                yield ("delim", "\\")
            else:
                self.state = IDENTIFIER_STATE
                self.reconsume_input_character()
        elif ch == "]":
            yield ("]",)
        elif ch == "{":
            yield ("{",)
        elif ch == "}":
            yield ("}",)
        elif is_digit(ch):
            self.state = NUMBER_STATE
            self.reconsume_input_character()
        elif ch == "U" or ch == "u":
            chs = self.next_input_character(3)
            if chs[0] == "+" and is_hex_digit(chs[1]):
                self.index += 1
                self.state = UNICODE_RANGE_STATE
            elif chs.lower() == "rl(":
                self.index += 3
                self.state = URL_STATE
            else:
                self.state = IDENTIFIER_STATE
                self.reconsume_input_character()
        elif is_name_start_character(ch):
            self.state = IDENTIFIER_STATE
            self.reconsume_input_character()
        elif self.index > len(self.s):
            yield ("EOF",)
        else:
            yield ("delim", ch)
    
    def double_quote_string_state(self):
        if self.tmp_string is None:
            self.tmp_string = ""
        ch = self.consume_next_input_character()
        if ch == "\"":
            yield ("string", self.tmp_string)
            self.tmp_string = None
            self.state = DATA_STATE
        elif self.index > len(self.s):
            yield ("EOF", )
        elif is_newline(ch):
            # @@@ parse error
            yield ("bad-string",)
            self.state = DATA_STATE
            self.reconsume_input_character()
        elif ch == "\\":
            if self.index > len(self.s):
                # @@@ parse error
                yield ("bad-string",)
                self.state = DATA_STATE
            elif is_newline(self.next_input_character()):
                self.index += 1
            else:
                self.tmp_string += self.consume_escaped_character()
        else:
            self.tmp_string += ch
    
    def single_quote_string_state(self):
        if self.tmp_string is None:
            self.tmp_string = ""
        ch = self.consume_next_input_character()
        if ch == "'":
            yield ("string", self.tmp_string)
            self.tmp_string = None
            self.state = DATA_STATE
        elif self.index > len(self.s):
            yield ("EOF", )
        elif is_newline(ch):
            # @@@ parse error
            yield ("bad-string",)
            self.state = DATA_STATE
            self.reconsume_input_character()
        elif ch == "\\":
            if self.index > len(self.s):
                # @@@ parse error
                yield ("bad-string",)
                self.state = DATA_STATE
            elif is_newline(self.next_input_character()):
                self.index += 1
            else:
                self.tmp_string += self.consume_escaped_character()
        else:
            self.tmp_string += ch
    
    def hash_state(self):
        ch = self.consume_next_input_character()
        if is_name_character(ch):
            self.tmp_hash = ch
            self.state = HASH_REST_STATE
        elif ch == "\\":
            if self.index > len(self.s) or is_newline(self.next_input_character()):
                yield ("delim", "#")
                self.state = DATA_STATE
                self.reconsume_input_character()
            else:
                self.tmp_hash = self.consume_escaped_character()
                self.state = HASH_REST_STATE
        else:
            yield ("delim", "#")
            self.state = DATA_STATE
            self.reconsume_input_character()
    
    def hash_rest_state(self):
        ch = self.consume_next_input_character()
        if is_name_character(ch):
            self.tmp_hash += ch
        elif ch == "\\":
            if self.index > len(self.s) or is_newline(self.next_input_character()):
                yield ("hash", self.tmp_hash)
                self.state = DATA_STATE
                self.reconsume_input_character()
            else:
                self.tmp_hash += self.consume_escaped_character()
        else:
            yield ("hash", self.tmp_hash)
            self.state = DATA_STATE
            self.reconsume_input_character()
    
    def comment_state(self):
        ch = self.consume_next_input_character()
        if ch == "*":
            if self.next_input_character() == "/":
                self.index += 1
                self.state = DATA_STATE
            else:
                pass
        elif self.index > len(self.s):
            # @@@ parse error
            self.state = DATA_STATE
            self.reconsume_input_character()
        else:
            pass
        return []  # @@@
    
    def at_keyword_state(self):
        ch = self.consume_next_input_character()
        ch2 = self.next_input_character()
        if ch == "-":
            if is_name_start_character(ch2):
                self.tmp_at_keyword = "-" + ch2
                self.index += 1
                self.state = AT_KEYWORD_REST_STATE
            else:
                yield ("delim", "@")
                self.state = DATA_STATE
                self.reconsume_input_character()
        elif is_name_start_character(ch):
            self.tmp_at_keyword = ch
            self.state = AT_KEYWORD_REST_STATE
        elif ch == "\\":
            if self.index > len(self.s) or is_newline(ch2):
                yield ("delim", "@")
                self.state = DATA_STATE
                self.reconsume_input_character()
            else:
                self.tmp_at_keyword = self.consume_escaped_character()
        else:
            yield ("delim", "@")
            self.state = DATA_STATE
            self.reconsume_input_character()
    
    def at_keyword_rest_state(self):
        ch = self.consume_next_input_character()
        ch2 = self.next_input_character()
        if is_name_character(ch):
            self.tmp_at_keyword += ch
        elif ch == "\\":
            if self.index > len(self.s) or is_newline(ch2):
                yield ("at", self.tmp_at_keyword)
                self.state = DATA_STATE
                self.reconsume_input_character()
            else:
                self.tmp_at_keyword += self.consume_escaped_character()
        else:
            yield ("at", self.tmp_at_keyword)
            self.state = DATA_STATE
            self.reconsume_input_character()
    
    def identifier_state(self):
        ch = self.consume_next_input_character()
        chs = self.next_input_character()
        if ch == "-":
            if is_name_start_character(chs):
                self.tmp_identifier = "-"
                self.state = IDENTIFIER_REST_STATE
            else:
                self.state = DATA_STATE
                self.reconsume_input_character()
        elif is_name_start_character(ch):
            self.tmp_identifier = ch
            self.state = IDENTIFIER_REST_STATE
        elif ch == "\\":
            if self.index > len(self.s) or is_newline(chs):
                self.state = DATA_STATE
                self.reconsume_input_character()
            else:
                self.tmp_identifier = self.consume_escaped_character()
                self.state = IDENTIFIER_REST_STATE
        else:
            self.state = DATA_STATE
            self.reconsume_input_character()
        return []  # @@@
    
    def identifier_rest_state(self):
        ch = self.consume_next_input_character()
        chs = self.next_input_character()
        if is_name_character(ch):
            self.tmp_identifier += ch
        elif ch == "\\":
            if self.index > len(self.s) or is_newline(chs):
                self.state = DATA_STATE
                self.reconsume_input_character()
            else:
                self.tmp_identifier += self.consume_escaped_character()
        elif ch == "(":
            yield ("function", self.tmp_identifier)
            self.state = DATA_STATE
        elif is_whitespace(ch):
            if self.transform_function_whitespace:
                self.state = TRANSFORM_FUNCTION_WHITESPACE_STATE
            else:
                yield ("identifier", self.tmp_identifier)
                self.state = DATA_STATE
                self.reconsume_input_character()
        else:
            yield ("identifier", self.tmp_identifier)
            self.state = DATA_STATE
            self.reconsume_input_character()
    
    def number_state(self):
        self.tmp_number = ""
        ch = self.consume_next_input_character()
        chs = self.next_input_character(2)
        if ch == "-":
            if is_digit(chs[0]):
                self.index += 1
                self.tmp_number += "-"
                self.tmp_number += chs[0]
                self.state = NUMBER_REST_STATE
            elif chs[0] == "." and is_digit(chs[1]):
                self.index += 2
                self.tmp_number += "-"
                self.tmp_number += "."
                self.tmp_number += chs[1]
                self.state = NUMBER_FRACTION_STATE
            else:
                self.state = DATA_STATE
                self.reconsume_input_character()
        elif ch == "+":
            if is_digit(chs[0]):
                self.index += 1
                self.tmp_number += "+"
                self.tmp_number += chs[0]
                self.state = NUMBER_REST_STATE
            elif chs[0] == "." and is_digit(chs[1]):
                self.index += 2
                self.tmp_number += "+"
                self.tmp_number += "."
                self.tmp_number += chs[1]
                self.state = NUMBER_FRACTION_STATE
            else:
                self.state = DATA_STATE
                self.reconsume_input_character()
        elif is_digit(ch):
            self.tmp_number += ch
            self.state = NUMBER_REST_STATE
        elif ch == ".":
            if is_digit(chs[0]):
                self.index += 1
                self.tmp_number += "."
                self.tmp_number += chs[0]
                self.state = NUMBER_FRACTION_STATE
            else:
                self.state = DATA_STATE
                self.reconsume_input_character()
        else:
            self.state = DATA_STATE
            self.reconsume_input_character()
        return []
    
    def number_rest_state(self):
        ch = self.consume_next_input_character()
        chs = self.next_input_character(2)
        if is_digit(ch):
            self.tmp_number += ch
        elif ch == ".":
            if is_digit(chs[0]):
                self.index += 1
                self.tmp_number += "."
                self.tmp_number += chs[0]
                self.state = NUMBER_FRACTION_STATE
            else:
                yield ("number", int(self.tmp_number))
                self.state = DATA_STATE
                self.reconsume_input_character()
        elif ch == "%":
            yield ("percentage", int(self.tmp_number))
            self.state = DATA_STATE
        elif ch.lower() == "e":
            if not self.supports_scientific_notation:
                self.tmp_dimension = (int(self.tmp_number), ch)  # @@@ int for now
                self.state = DIMENSION_STATE
            else:
                xxx
        elif ch == "-":
            xxx
        elif is_name_start_character(ch):
            self.tmp_dimension = (int(self.tmp_number), ch)  # @@@ int for now
            self.state = DIMENSION_STATE
        elif ch == "\\":
            xxx
        else:
            yield ("number", int(self.tmp_number))  # @@@ int for now
            self.state = DATA_STATE
            self.reconsume_input_character()
    
    def number_fraction_state(self):
        ch = self.consume_next_input_character()
        if is_digit(ch):
            self.tmp_number += ch
        elif ch == ".":
            yield ("number", float(self.tmp_number))
            self.state = DATA_STATE
            self.reconsume_input_character()
        elif ch == "%":
            xxx
        elif ch.lower() == "e":
            if not self.supports_scientific_notation:
                self.tmp_dimension = (float(self.tmp_number), ch)
                self.state = DIMENSION_STATE
            else:
                xxx
        elif ch == "-":
            xxx
        elif is_name_start_character(ch):
            self.tmp_dimension = (float(self.tmp_number), ch)
            self.state = DIMENSION_STATE
        elif ch == "\\":
            xxx
        else:
            yield ("number", float(self.tmp_number))
            self.state = DATA_STATE
            self.reconsume_input_character()
        
    def dimension_state(self):
        ch = self.consume_next_input_character()
        if is_name_character(ch):
            num, unit = self.tmp_dimension
            unit += ch
            self.tmp_dimension = num, unit
        elif ch == "\\":
            xxx
        else:
            yield ("dimension", self.tmp_dimension[0], self.tmp_dimension[1])
            self.state = DATA_STATE
            self.reconsume_input_character()
