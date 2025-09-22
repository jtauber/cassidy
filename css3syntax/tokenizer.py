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


def is_non_ascii_ident_code_point(ch):
    return any([
        ch == "\u00B7",
        "\u00C0" <= ch <= "\u00D6",
        "\u00D8" <= ch <= "\u00F6",
        "\u00F8" <= ch <= "\u037D",
        "\u037F" <= ch <= "\u1FFF",
        "\u200C" <= ch <= "\u200D",
        "\u203F" <= ch <= "\u2040",
        "\u2070" <= ch <= "\u218F",
        "\u2C00" <= ch <= "\u2FEF",
        "\u3001" <= ch <= "\uD7FF",
        "\uF900" <= ch <= "\uFDCF",
        "\uFDF0" <= ch <= "\uFFFD",
        ch >= "\U00010000",
    ])


def is_ident_start_code_point(ch):
    return is_letter(ch) or is_non_ascii_ident_code_point(ch) or ch == "\u005F"  # _


def is_ident_code_point(ch):
    return is_ident_start_code_point(ch) or is_digit(ch) or ch == "\u002D"  # -


def is_non_printable_code_point(ch):
    return any([
        "\u0000" <= ch <= "\u0008",
        ch == "\u000B",
        "\u000E" <= ch <= "\u001F",
        ch == "\u007F",
    ])


def is_newline(ch):
    return ch == "\u000A"
    # carriage return and form feed removed in preprocessing


def is_whitespace(ch):
    return any([
        is_newline(ch),
        ch == "\u0009",
        ch == "\u0020"
    ])


def is_surrogate(code_point):
    return 0xD800 <= code_point <= 0xDFFF


# 4.3.8
def are_a_valid_escape(ch_pair):
    return ch_pair[0] == "\\" and ch_pair[1] != "\n"


# 4.3.9
def would_start_ident_sequence(ch_triplet):
    if ch_triplet[0] == "\u002D":
        if any([
            is_ident_start_code_point(ch_triplet[1]),
            ch_triplet[1] == "\u002D",
            are_a_valid_escape(ch_triplet[1:3])
        ]):
            return True
        else:
            return False
    elif is_ident_start_code_point(ch_triplet[0]):
        return True
    elif ch_triplet[0] == "\\":
        if are_a_valid_escape(ch_triplet[0:2]):
            return True
        else:
            return False
    else:
        return False


# 4.3.10
def start_number(ch_triplet):
    if ch_triplet[0] == "\u002B" or ch_triplet[0] == "\u002D":
        if is_digit(ch_triplet[1]):
            return True
        elif ch_triplet[1] == "." and is_digit(ch_triplet[2]):
            return True
        else:
            return False
    elif ch_triplet[0] == ".":
        if is_digit(ch_triplet[1]):
            return True
        else:
            return False
    elif is_digit(ch_triplet[0]):
        return True
    else:
        return False


# 4.3.11
def start_unicode_range(ch_triplet):
    return all([
        ch_triplet[0] in ("U", "u"),
        ch_triplet[1] == "+",
        ch_triplet[2] == "\u003F" or is_hex_digit(ch_triplet[2])
    ])


MAXIMUM_ALLOWED_CODE_POINT = 0x10FFFF

WHITESPACE_TOKEN = "WS"
HASH_TOKEN = "HASH"
DELIM_TOKEN = "DELIM"
OPEN_PAREN_TOKEN = "OPEN-PAREN"
CLOSE_PAREN_TOKEN = "CLOSE-PAREN"
CDC_TOKEN = "CDC"
CDO_TOKEN = "CDO"
COLON_TOKEN = "COLON"
SEMICOLON_TOKEN = "SEMICOLON"
AT_KEYWORD_TOKEN = "AT"
OPEN_SQUARE_TOKEN = "OPEN-SQUARE"
CLOSE_SQUARE_TOKEN = "CLOSE-SQUARE"
OPEN_CURLY_TOKEN = "OPEN-CURLY"
CLOSE_CURLY_TOKEN = "CLOSE-CURLY"
BAD_URL_TOKEN = "BAD-URL"
URL_TOKEN = "URL"
EOF_TOKEN = "EOF"
FUNCTION_TOKEN = "FUNCTION"
STRING_TOKEN = "STRING"
BAD_STRING_TOKEN = "BAD-STRING"
IDENT_TOKEN = "IDENT"
NUMBER_TOKEN = "NUMBER"
DIMENSION_TOKEN = "DIM"
PERCENTAGE_TOKEN = "PERCENTAGE"
UNICODE_RANGE_TOKEN = "UNICODE-RANGE"
COMMA_TOKEN = "COMMA"


class Tokenizer:

    def __init__(self, unicode_ranges_allowed=False):
        self.unicode_ranges_allowed = unicode_ranges_allowed

    def tokenize(self, s):
        self.s = s
        self.index = 0

        while True:
            token = self.consume_a_token(self.unicode_ranges_allowed)
            yield token
            if token[0] == EOF_TOKEN:
                break

    def consume_next_input_code_point(self):
        if self.index >= len(self.s):
            ch = None
        else:
            ch = self.s[self.index]
            self.index += 1

        return ch

    def consume_whitespace(self):
        while self.index < len(self.s) and is_whitespace(self.s[self.index]):
            self.index += 1

    def next_input_code_point(self, size=1):
        return self.s[self.index:self.index + size]

    def reconsume_input_code_point(self):
        self.index -= 1

    # 4.3.1
    def consume_a_token(self, unicode_ranges_allowed=False):

        self.consume_comments()

        ch = self.consume_next_input_code_point()

        if ch is None:
            return (EOF_TOKEN,)

        elif is_whitespace(ch):
            self.consume_whitespace()
            return (WHITESPACE_TOKEN,)

        elif ch == "\"":
            return self.consume_a_string_token("\"")

        elif ch == "#":
            if (is_ident_code_point(self.next_input_code_point())
                or are_a_valid_escape(self.next_input_code_point(2))
            ):
                type_flag = "unrestricted"
                if would_start_ident_sequence(self.next_input_code_point(3)):
                    type_flag = "id"
                tmp = self.consume_an_ident_sequence()
                return (HASH_TOKEN, tmp, type_flag)
            else:
                return (DELIM_TOKEN, self.consume_next_input_code_point())

        elif ch == "'":
            return self.consume_a_string_token("'")

        elif ch == "(":
            return (OPEN_PAREN_TOKEN,)

        elif ch == ")":
            return (CLOSE_PAREN_TOKEN,)

        elif ch == "+":
            if start_number(self.next_input_code_point(3)):
                self.reconsume_input_code_point()
                return self.consume_a_numeric_token()
            else:
                return (DELIM_TOKEN, ch)

        elif ch == ",":
            return (COMMA_TOKEN,)

        elif ch == "-":
            if start_number(self.next_input_code_point(3)):
                self.reconsume_input_code_point()
                return self.consume_a_numeric_token()
            elif self.next_input_code_point(2) == "->":
                self.index += 2
                return (CDC_TOKEN,)
            elif would_start_ident_sequence(self.next_input_code_point(3)):
                self.reconsume_input_code_point()
                return self.consume_an_ident_like_token()
            else:
                return (DELIM_TOKEN, ch)

        elif ch == ".":
            if start_number(self.next_input_code_point(3)):
                self.reconsume_input_code_point()
                return self.consume_a_numeric_token()
            else:
                return (DELIM_TOKEN, ch)

        elif ch == ":":
            return (COLON_TOKEN,)

        elif ch == ";":
            return (SEMICOLON_TOKEN,)

        elif ch == "<":
            if self.next_input_code_point(3) == "!--":
                self.index += 3
                return (CDO_TOKEN,)
            else:
                return (DELIM_TOKEN, ch)

        elif ch == "@":
            if would_start_ident_sequence(self.next_input_code_point(3)):
                return (AT_KEYWORD_TOKEN, self.consume_an_ident_sequence())
            else:
                return (DELIM_TOKEN, ch)

        elif ch == "[":
            return (OPEN_SQUARE_TOKEN,)

        elif ch == "\\":
            if are_a_valid_escape(self.next_input_code_point(2)):
                self.reconsume_input_code_point()
                return self.consume_an_ident_like_token()
            else:
                # @@@ parse error
                return (DELIM_TOKEN, ch)

        elif ch == "]":
            return (CLOSE_SQUARE_TOKEN,)

        elif ch == "{":
            return (OPEN_CURLY_TOKEN,)

        elif ch == "}":
            return (CLOSE_CURLY_TOKEN,)

        elif is_digit(ch):
            self.reconsume_input_code_point()
            return self.consume_a_numeric_token()

        elif ch == "U" or ch == "u":
            if unicode_ranges_allowed and start_unicode_range(self.next_input_code_point(3)):
                self.reconsume_input_code_point()
                return self.consume_a_unicode_range_token()
            else:
                self.reconsume_input_code_point()
                return self.consume_an_ident_like_token()

        elif is_ident_start_code_point(ch):
            self.reconsume_input_code_point()
            return self.consume_an_ident_like_token()

        else:
            return (DELIM_TOKEN, ch)

    # 4.3.2
    def consume_comments(self):
        while True:
            if self.next_input_code_point(2) == "/*":
                self.index += 2
                while True:
                    if self.next_input_code_point(2) == "*/":
                        self.index += 2
                        break
                    elif self.index >= len(self.s):
                        # @@@ parse error
                        break
                    else:
                        self.index += 1
            else:
                break

    # 4.3.3
    def consume_a_numeric_token(self):
        number = self.consume_a_number()
        if would_start_ident_sequence(self.next_input_code_point(3)):
            tmp_ident = self.consume_an_ident_sequence()
            return (DIMENSION_TOKEN, number[0], number[1], number[2], tmp_ident)
        elif self.next_input_code_point() == "%":
            self.index += 1
            return (PERCENTAGE_TOKEN, number[0], number[2])
        else:
            return (NUMBER_TOKEN, number[0], number[1], number[2])

    # 4.3.4
    def consume_an_ident_like_token(self):
        string = self.consume_an_ident_sequence()
        if string.lower() == "url" and self.next_input_code_point() == "(":
            self.index += 1
            while True:
                next_two = self.next_input_code_point(2)
                if is_whitespace(next_two[0]) and is_whitespace(next_two[1]):
                    self.index += 1
                    continue
                else:
                    break
            if any([
                self.next_input_code_point() == "\"",
                self.next_input_code_point() == "'",
                is_whitespace(self.next_input_code_point()) and self.next_input_code_point(2)[1] == "\"",
                is_whitespace(self.next_input_code_point()) and self.next_input_code_point(2)[1] == "'",
            ]):
                return (FUNCTION_TOKEN, string)
            else:
                return self.consume_a_url_token()
        elif self.next_input_code_point() == "(":
            self.index += 1
            return (FUNCTION_TOKEN, string)
        else:
            return (IDENT_TOKEN, string)

    # 4.3.5
    def consume_a_string_token(self, ending_code_point):
        string = ""
        while True:
            ch = self.consume_next_input_code_point()
            if ch == ending_code_point:
                return (STRING_TOKEN, string)
            elif ch is None:
                # @@@ parse error
                return (EOF_TOKEN,)
            elif is_newline(ch):
                # @@@ parse error
                self.reconsume_input_code_point()
                return (BAD_STRING_TOKEN,)
            elif ch == "\\":
                if self.index >= len(self.s):
                    continue
                elif is_newline(self.next_input_code_point()):
                    self.index += 1
                else:
                    string += self.consume_an_escaped_code_point()
            else:
                string += ch

    # 4.3.6
    def consume_a_url_token(self):
        string = ""
        self.consume_whitespace()
        while True:
            ch = self.consume_next_input_code_point()
            if ch == ")":
                return (URL_TOKEN, string)
            elif ch is None:
                # @@@ parse error
                return (EOF_TOKEN,)
            elif is_whitespace(ch):
                self.consume_whitespace()
                if self.next_input_code_point() == ")":
                    self.index += 1
                    return (URL_TOKEN, string)
                elif self.index >= len(self.s):
                    # @@@ parse error
                    return (URL_TOKEN, string)
                else:
                    # @@@ parse error
                    return (BAD_URL_TOKEN, self.consume_remnant_of_a_bad_url())
            elif any([
                ch == "\"",
                ch == "'",
                ch == "(",
                is_non_printable_code_point(ch)
            ]):
                # @@@ parse error
                return (BAD_URL_TOKEN, self.consume_remnant_of_a_bad_url())
            elif ch == "\\":
                if are_a_valid_escape(self.next_input_code_point(2)):
                    string += self.consume_an_escaped_code_point()
                else:
                    # @@@ parse error
                    return (BAD_URL_TOKEN, self.consume_remnant_of_a_bad_url())
            else:
                string += ch

    # 4.3.7
    def consume_an_escaped_code_point(self):
        ch = self.consume_next_input_code_point()
        if ch is None:
            # @@@ parse error
            return "\uFFFD"
        elif is_hex_digit(ch):
            digits = ch
            while len(digits) < 6:
                ch = self.consume_next_input_code_point()
                if is_hex_digit(ch):
                    digits += ch
                elif is_whitespace(ch):
                    break
                else:
                    self.reconsume_input_code_point()
                    break
            code_point = int(digits, 16)
            if code_point > MAXIMUM_ALLOWED_CODE_POINT or code_point == 0 or is_surrogate(code_point):
                return "\uFFFD"
            else:
                return chr(code_point)
        else:
            return ch

    # 4.3.12
    def consume_an_ident_sequence(self):
        result = ""
        while True:
            ch = self.consume_next_input_code_point()
            if ch is None:  # is this case described in spec?
                break
            if is_ident_code_point(ch):
                result += ch
            elif are_a_valid_escape(self.next_input_code_point(2)):
                result += self.consume_an_escaped_code_point()
            else:
                self.reconsume_input_code_point()
                break
        return result

    # 4.3.13
    def consume_a_number(self):
        _type = "integer"
        number_part = ""
        exponent_part = ""
        sign_character = ""
        tmp = self.next_input_code_point()
        if tmp == "+" or tmp == "-":
            sign_character = tmp
            number_part += sign_character
            self.index += 1
        while True:
            tmp = self.next_input_code_point()
            if is_digit(tmp):
                number_part += tmp
                self.index += 1
            else:
                break
        if self.next_input_code_point() == "." and is_digit(self.next_input_code_point(2)[1]):
            _type = "number"
            number_part += "."
            self.index += 1
            while True:
                tmp = self.next_input_code_point()
                if is_digit(tmp):
                    number_part += tmp
                    self.index += 1
                else:
                    break
        if any([
            self.next_input_code_point() in ("E", "e") and is_digit(self.next_input_code_point(2)[1]),
            self.next_input_code_point(2) in ("E+", "E-", "e+", "e-") and is_digit(self.next_input_code_point(3)[2])
        ]):
            self.consume_next_input_code_point()  # E or e
            tmp = self.next_input_code_point()
            if tmp == "+" or tmp == "-":
                exponent_part += tmp
                self.index += 1
            while True:
                tmp = self.next_input_code_point()
                if is_digit(tmp):
                    exponent_part += tmp
                    self.index += 1
                else:
                    break
            _type = "number"
        if exponent_part:
            value = float(number_part) * (10 ** int(exponent_part))
        else:
            if _type == "integer":
                value = int(number_part)
            else:
                value = float(number_part)

        return (value, _type, sign_character)

    # 4.3.14
    # "due to a bad syntax design in early CSS"
    def consume_a_unicode_range_token(self):
        self.consume_next_input_code_point()
        self.consume_next_input_code_point()
        first_segment = ""
        while True:
            ch = self.consume_next_input_code_point()
            if ch is None:
                break  # is this described in spec?
            elif is_hex_digit(ch):
                first_segment += ch
                if len(first_segment) == 6:
                    break
        if len(first_segment) < 6:
            while True:
                ch = self.consume_next_input_code_point()
                if ch is None:
                    break  # is this described in spec?
                elif ch == "\u003F":  # ?
                    first_segment += ch
                    if len(first_segment) == 6:
                        break
                else:
                    self.reconsume_input_code_point()
                    break
        if "?" in first_segment:
            start_of_range = int(first_segment.replace("?", "0"), 16)
            end_of_range = int(first_segment.replace("?", "F"), 16)
            return (UNICODE_RANGE_TOKEN, start_of_range, end_of_range)
        start_of_range = int(first_segment, 16)
        if self.next_input_code_point() == "-" and is_hex_digit(self.next_input_code_point(2)[1]):
            self.index += 1
            second_segment = ""
            while True:
                ch = self.consume_next_input_code_point()
                if ch is None:
                    break  # is this described in spec?
                elif is_hex_digit(ch):
                    second_segment += ch
                    if len(second_segment) == 6:
                        break
                else:
                    self.reconsume_input_code_point()
                    break
            end_of_range = int(second_segment, 16)
            return (UNICODE_RANGE_TOKEN, start_of_range, end_of_range)
        else:
            return (UNICODE_RANGE_TOKEN, start_of_range, start_of_range)

    # 4.3.15
    def consume_remnant_of_a_bad_url(self):
        while True:
            ch = self.consume_next_input_code_point()
            if ch is None or ch == ")":
                return
            elif are_a_valid_escape(self.next_input_code_point(2)):
                self.consume_an_escaped_code_point()
            else:
                continue
