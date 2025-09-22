from dataclasses import dataclass
from typing import Generator, Literal


def is_digit(ch: str) -> bool:
    return "0" <= ch <= "9"


def is_hex_digit(ch: str) -> bool:
    return is_digit(ch) or "A" <= ch <= "F" or "a" <= ch <= "f"


def is_uppercase_letter(ch: str) -> bool:
    return "A" <= ch <= "Z"


def is_lowercase_letter(ch: str) -> bool:
    return "a" <= ch <= "z"


def is_letter(ch: str) -> bool:
    return is_uppercase_letter(ch) or is_lowercase_letter(ch)


def is_non_ascii_ident_code_point(ch: str) -> bool:
    return any(
        [
            ch == "\u00b7",
            "\u00c0" <= ch <= "\u00d6",
            "\u00d8" <= ch <= "\u00f6",
            "\u00f8" <= ch <= "\u037d",
            "\u037f" <= ch <= "\u1fff",
            "\u200c" <= ch <= "\u200d",
            "\u203f" <= ch <= "\u2040",
            "\u2070" <= ch <= "\u218f",
            "\u2c00" <= ch <= "\u2fef",
            "\u3001" <= ch <= "\ud7ff",
            "\uf900" <= ch <= "\ufdcf",
            "\ufdf0" <= ch <= "\ufffd",
            ch >= "\U00010000",
        ]
    )


def is_ident_start_code_point(ch: str) -> bool:
    return is_letter(ch) or is_non_ascii_ident_code_point(ch) or ch == "\u005f"  # _


def is_ident_code_point(ch: str) -> bool:
    return is_ident_start_code_point(ch) or is_digit(ch) or ch == "\u002d"  # -


def is_non_printable_code_point(ch: str) -> bool:
    return any(
        [
            "\u0000" <= ch <= "\u0008",
            ch == "\u000b",
            "\u000e" <= ch <= "\u001f",
            ch == "\u007f",
        ]
    )


def is_newline(ch: str) -> bool:
    return ch == "\u000a"
    # carriage return and form feed removed in preprocessing


def is_whitespace(ch: str) -> bool:
    return any([is_newline(ch), ch == "\u0009", ch == "\u0020"])


def is_surrogate(code_point: int) -> bool:
    return 0xD800 <= code_point <= 0xDFFF


# 4.3.8
def are_a_valid_escape(ch_pair: str) -> bool:
    return ch_pair[0] == "\\" and ch_pair[1] != "\n"


# 4.3.9
def would_start_ident_sequence(ch_triplet: str) -> bool:
    if ch_triplet[0] == "\u002d":
        if any(
            [
                is_ident_start_code_point(ch_triplet[1]),
                ch_triplet[1] == "\u002d",
                are_a_valid_escape(ch_triplet[1:3]),
            ]
        ):
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
def start_number(ch_triplet: str) -> bool:
    if ch_triplet[0] == "\u002b" or ch_triplet[0] == "\u002d":
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
def start_unicode_range(ch_triplet: str) -> bool:
    return all(
        [
            ch_triplet[0] in ("U", "u"),
            ch_triplet[1] == "+",
            ch_triplet[2] == "\u003f" or is_hex_digit(ch_triplet[2]),
        ]
    )


MAXIMUM_ALLOWED_CODE_POINT = 0x10FFFF


class Token:
    pass


class WhitespaceToken(Token):
    def __str__(self):
        return f"WS"


class EofToken(Token):
    def __str__(self):
        return f"EOF"


class OpenCurlyToken(Token):
    def __str__(self):
        return f"OPEN-CURLY"


class CloseCurlyToken(Token):
    def __str__(self):
        return f"CLOSE-CURLY"


class ColonToken(Token):
    def __str__(self):
        return f"COLON"


class SemicolonToken(Token):
    def __str__(self):
        return f"SEMICOLON"


class OpenParen(Token):
    def __str__(self):
        return f"OPEN-PAREN"


class CloseParen(Token):
    def __str__(self):
        return f"CLOSE-PAREN"


class CommaToken(Token):
    def __str__(self):
        return f"COMMA"


class OpenSquareToken(Token):
    def __str__(self):
        return f"OPEN-SQUARE"


class CloseSquareToken(Token):
    def __str__(self):
        return f"CLOSE-SQUARE"


class CdoToken(Token):
    def __str__(self):
        return f"CDO"


class CdcToken(Token):
    def __str__(self):
        return f"CDC"


@dataclass
class IdentToken(Token):
    value: str

    def __str__(self):
        return f"IDENT({self.value})"


@dataclass
class DelimToken(Token):
    value: str

    def __str__(self):
        return f"DELIM({self.value})"


@dataclass
class AtKeywordToken(Token):
    value: str

    def __str__(self):
        return f"AT({self.value})"


@dataclass
class StringToken(Token):
    value: str

    def __str__(self):
        return f"STRING({self.value})"


class BadStringToken(Token):
    def __str__(self):
        return f"@@@"


@dataclass
class FunctionToken(Token):
    value: str

    def __str__(self):
        return f"FUNCTION({self.value})"


@dataclass
class UrlToken(Token):
    value: str

    def __str__(self):
        return f"URL({self.value})"


@dataclass
class BadUrlToken(Token):
    def __str__(self):
        return f"@@@"


@dataclass
class HashToken(Token):
    value: str
    type_flag: Literal["id", "unrestricted"]

    def __str__(self):
        return f"HASH({self.value})"


@dataclass
class PercentageToken(Token):
    value: float
    sign_character: Literal["", "+", "-"]

    def __str__(self):
        sign_str = self.sign_character if self.sign_character == "+" else ""
        return f"PERCENTAGE({sign_str}{self.value})"


# @@@ could split this into separate integer/number classes
@dataclass
class NumberToken(Token):
    value: int | float
    type_flag: Literal["integer", "number"]
    sign_character: Literal["", "+", "-"]

    def __str__(self):
        sign_str = self.sign_character if self.sign_character == "+" else ""
        if self.type_flag == "integer":
            return f"INT({sign_str}{self.value})"
        else:
            return f"NUMBER({sign_str}{self.value})"


# @@@ could split this into separate integer/number classes
@dataclass
class DimensionToken(Token):
    value: int | float
    type_flag: Literal["integer", "number"]
    sign_character: Literal["", "+", "-"]
    unit: str

    def __str__(self):
        sign_str = self.sign_character if self.sign_character == "+" else ""
        return f"DIM({sign_str}{self.value}, {self.unit})"


@dataclass
class UnicodeRangeToken(Token):
    start: int
    end: int

    def __str__(self):
        if self.start == self.end:
            return f"UNICODE-RANGE({hex(self.start)})"
        else:
            return f"UNICODE-RANGE({hex(self.start)}-{hex(self.end)})"


class Tokenizer:
    def __init__(self, unicode_ranges_allowed=False):
        self.unicode_ranges_allowed = unicode_ranges_allowed

    def tokenize(self, s: str) -> Generator[Token]:
        self.s = s
        self.index = 0

        while True:
            token = self.consume_a_token(self.unicode_ranges_allowed)
            yield token
            if isinstance(token, EofToken):
                break

    def consume_next_input_code_point(self) -> str | None:
        if self.index >= len(self.s):
            ch = None
        else:
            ch = self.s[self.index]
            self.index += 1

        return ch

    def consume_whitespace(self) -> None:
        while self.index < len(self.s) and is_whitespace(self.s[self.index]):
            self.index += 1

    def next_input_code_point(self, size=1) -> str:
        return self.s[self.index : self.index + size]

    def reconsume_input_code_point(self) -> None:
        self.index -= 1

    # 4.3.1
    def consume_a_token(self, unicode_ranges_allowed: bool = False) -> Token:
        self.consume_comments()

        ch = self.consume_next_input_code_point()

        if ch is None:
            return EofToken()

        elif is_whitespace(ch):
            self.consume_whitespace()
            return WhitespaceToken()

        elif ch == '"':
            return self.consume_a_string_token('"')

        elif ch == "#":
            if is_ident_code_point(self.next_input_code_point()) or are_a_valid_escape(
                self.next_input_code_point(2)
            ):
                return HashToken(
                    self.consume_an_ident_sequence(),
                    type_flag="id"
                    if would_start_ident_sequence(self.next_input_code_point(3))
                    else "unrestricted",
                )
            else:
                value = self.consume_next_input_code_point()
                if value is not None:
                    return DelimToken(value)
                else:
                    return EofToken()  # is this case described in spec?

        elif ch == "'":
            return self.consume_a_string_token("'")

        elif ch == "(":
            return OpenParen()

        elif ch == ")":
            return CloseParen()

        elif ch == "+":
            if start_number(self.next_input_code_point(3)):
                self.reconsume_input_code_point()
                return self.consume_a_numeric_token()
            else:
                return DelimToken(ch)

        elif ch == ",":
            return CommaToken()

        elif ch == "-":
            if start_number(self.next_input_code_point(3)):
                self.reconsume_input_code_point()
                return self.consume_a_numeric_token()
            elif self.next_input_code_point(2) == "->":
                self.index += 2
                return CdcToken()
            elif would_start_ident_sequence(self.next_input_code_point(3)):
                self.reconsume_input_code_point()
                return self.consume_an_ident_like_token()
            else:
                return DelimToken(ch)

        elif ch == ".":
            if start_number(self.next_input_code_point(3)):
                self.reconsume_input_code_point()
                return self.consume_a_numeric_token()
            else:
                return DelimToken(ch)

        elif ch == ":":
            return ColonToken()

        elif ch == ";":
            return SemicolonToken()

        elif ch == "<":
            if self.next_input_code_point(3) == "!--":
                self.index += 3
                return CdoToken()
            else:
                return DelimToken(ch)

        elif ch == "@":
            if would_start_ident_sequence(self.next_input_code_point(3)):
                return AtKeywordToken(self.consume_an_ident_sequence())
            else:
                return DelimToken(ch)

        elif ch == "[":
            return OpenSquareToken()

        elif ch == "\\":
            if are_a_valid_escape(self.next_input_code_point(2)):
                self.reconsume_input_code_point()
                return self.consume_an_ident_like_token()
            else:
                # @@@ parse error
                return DelimToken(ch)

        elif ch == "]":
            return CloseSquareToken()

        elif ch == "{":
            return OpenCurlyToken()

        elif ch == "}":
            return CloseCurlyToken()

        elif is_digit(ch):
            self.reconsume_input_code_point()
            return self.consume_a_numeric_token()

        elif ch == "U" or ch == "u":
            if unicode_ranges_allowed and start_unicode_range(
                self.next_input_code_point(3)
            ):
                self.reconsume_input_code_point()
                return self.consume_a_unicode_range_token()
            else:
                self.reconsume_input_code_point()
                return self.consume_an_ident_like_token()

        elif is_ident_start_code_point(ch):
            self.reconsume_input_code_point()
            return self.consume_an_ident_like_token()

        else:
            return DelimToken(ch)

    # 4.3.2
    def consume_comments(self) -> None:
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
    def consume_a_numeric_token(self) -> NumberToken | PercentageToken | DimensionToken:
        number = self.consume_a_number()
        if would_start_ident_sequence(self.next_input_code_point(3)):
            tmp_ident = self.consume_an_ident_sequence()
            return DimensionToken(number[0], number[1], number[2], tmp_ident)
        elif self.next_input_code_point() == "%":
            self.index += 1
            return PercentageToken(number[0], number[2])
        else:
            return NumberToken(number[0], number[1], number[2])

    # 4.3.4
    def consume_an_ident_like_token(
        self,
    ) -> IdentToken | FunctionToken | UrlToken | BadUrlToken | EofToken:
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
            if any(
                [
                    self.next_input_code_point() == '"',
                    self.next_input_code_point() == "'",
                    is_whitespace(self.next_input_code_point())
                    and self.next_input_code_point(2)[1] == '"',
                    is_whitespace(self.next_input_code_point())
                    and self.next_input_code_point(2)[1] == "'",
                ]
            ):
                return FunctionToken(string)
            else:
                return self.consume_a_url_token()
        elif self.next_input_code_point() == "(":
            self.index += 1
            return FunctionToken(string)
        else:
            return IdentToken(string)

    # 4.3.5
    def consume_a_string_token(
        self, ending_code_point
    ) -> StringToken | BadStringToken | EofToken:
        string = ""
        while True:
            ch = self.consume_next_input_code_point()
            if ch == ending_code_point:
                return StringToken(string)
            elif ch is None:
                # @@@ parse error
                return EofToken()
            elif is_newline(ch):
                # @@@ parse error
                self.reconsume_input_code_point()
                return BadStringToken()
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
    def consume_a_url_token(self) -> UrlToken | BadUrlToken | EofToken:
        string = ""
        self.consume_whitespace()
        while True:
            ch = self.consume_next_input_code_point()
            if ch == ")":
                return UrlToken(string)
            elif ch is None:
                # @@@ parse error
                return EofToken()
            elif is_whitespace(ch):
                self.consume_whitespace()
                if self.next_input_code_point() == ")":
                    self.index += 1
                    return UrlToken(string)
                elif self.index >= len(self.s):
                    # @@@ parse error
                    return UrlToken(string)
                else:
                    # @@@ parse error
                    self.consume_remnant_of_a_bad_url()
                    return BadUrlToken()
            elif any(
                [ch == '"', ch == "'", ch == "(", is_non_printable_code_point(ch)]
            ):
                # @@@ parse error
                self.consume_remnant_of_a_bad_url()
                return BadUrlToken()
            elif ch == "\\":
                if are_a_valid_escape(self.next_input_code_point(2)):
                    string += self.consume_an_escaped_code_point()
                else:
                    # @@@ parse error
                    self.consume_remnant_of_a_bad_url()
                    return BadUrlToken()
            else:
                string += ch

    # 4.3.7
    def consume_an_escaped_code_point(self) -> str:
        ch = self.consume_next_input_code_point()
        if ch is None:
            # @@@ parse error
            return "\ufffd"
        elif is_hex_digit(ch):
            digits = ch
            while len(digits) < 6:
                ch = self.consume_next_input_code_point()
                if ch is None:
                    break  # is this case described in spec?
                elif is_hex_digit(ch):
                    digits += ch
                elif is_whitespace(ch):
                    break
                else:
                    self.reconsume_input_code_point()
                    break
            code_point = int(digits, 16)
            if (
                code_point > MAXIMUM_ALLOWED_CODE_POINT
                or code_point == 0
                or is_surrogate(code_point)
            ):
                return "\ufffd"
            else:
                return chr(code_point)
        else:
            return ch

    # 4.3.12
    def consume_an_ident_sequence(self) -> str:
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
    def consume_a_number(self) -> tuple:
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
        if self.next_input_code_point() == "." and is_digit(
            self.next_input_code_point(2)[1]
        ):
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
        if any(
            [
                self.next_input_code_point() in ("E", "e")
                and is_digit(self.next_input_code_point(2)[1]),
                self.next_input_code_point(2) in ("E+", "E-", "e+", "e-")
                and is_digit(self.next_input_code_point(3)[2]),
            ]
        ):
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
    def consume_a_unicode_range_token(self) -> UnicodeRangeToken:
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
                elif ch == "\u003f":  # ?
                    first_segment += ch
                    if len(first_segment) == 6:
                        break
                else:
                    self.reconsume_input_code_point()
                    break
        if "?" in first_segment:
            start_of_range = int(first_segment.replace("?", "0"), 16)
            end_of_range = int(first_segment.replace("?", "F"), 16)
            return UnicodeRangeToken(start_of_range, end_of_range)
        start_of_range = int(first_segment, 16)
        if self.next_input_code_point() == "-" and is_hex_digit(
            self.next_input_code_point(2)[1]
        ):
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
            return UnicodeRangeToken(start_of_range, end_of_range)
        else:
            return UnicodeRangeToken(start_of_range, start_of_range)

    # 4.3.15
    def consume_remnant_of_a_bad_url(self) -> None:
        while True:
            ch = self.consume_next_input_code_point()
            if ch is None or ch == ")":
                return
            elif are_a_valid_escape(self.next_input_code_point(2)):
                self.consume_an_escaped_code_point()
            else:
                continue
