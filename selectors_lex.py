import ply.lex as lex

ident = r"(-)?([a-z_]|[^\0-\177]|\\[0-9a-f]{1,6}(\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9a-f])([a-z0-9_\-]|[^\0-\177]|\\[0-9a-f]{1,6}(\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9a-f])*"
name = r"([a-z0-9_\-]|[^\0-\177]|\\[0-9a-f]{1,6}(\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9a-f]+)"

num = r"[0-9]+|[0-9]*\.[0-9]+"

string1 = r"\"([^\n\r\f\\\"]|\\(\n|\r\n|\r|\f)|[^\0-\177]|\\[0-9a-f]{1,6}(\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9a-f])*\""
string2 = r"\'([^\n\r\f\\\']|\\(\n|\r\n|\r|\f)|[^\0-\177]|\\[0-9a-f]{1,6}(\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9a-f])*\'"
string = string1 + r"|" + string2

invalid1 = r"\"([^\n\r\f\\\"]|\\(\n|\r\n|\r|\f)|[^\0-\177]|\\[0-9a-f]{1,6}(\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9a-f])*"
invalid2 = r"\'([^\n\r\f\\\']|\\(\n|\r\n|\r|\f)|[^\0-\177]|\\[0-9a-f]{1,6}(\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9a-f])*"
invalid = invalid1 + r"|" + invalid2

w = r"[ \t\r\n\f]*"

# D         d|\\0{0,4}(44|64)(\r\n|[ \t\r\n\f])?
# E         e|\\0{0,4}(45|65)(\r\n|[ \t\r\n\f])?
# N         n|\\0{0,4}(4e|6e)(\r\n|[ \t\r\n\f])?|\\n
# O         o|\\0{0,4}(4f|6f)(\r\n|[ \t\r\n\f])?|\\o
# T         t|\\0{0,4}(54|74)(\r\n|[ \t\r\n\f])?|\\t
# V         v|\\0{0,4}(58|78)(\r\n|[ \t\r\n\f])?|\\v

# %%

tokens = [
    "S",
    "INCLUDES",
    "DASHMATCH",
    "PREFIXMATCH",
    "SUFFIXMATCH",
    "SUBSTRINGMATCH",
    "IDENT",
    "STRING",
    "FUNCTION",
    "NUMBER",
    "HASH",
    "PLUS",
    "GREATER",
    "COMMA",
    "TILDE",
    "NOT",
    "ATKEYWORD",
    "INVALID",
    "PERCENTAGE",
    "DIMENSION",
    "CDO",
    "CDC",
]

literals = "*|.[=]:)"

t_S = r"[ \t\r\n\f]+"
t_INCLUDES = r"~="
t_DASHMATCH = r"\|="
t_PREFIXMATCH = r"\^="
t_SUFFIXMATCH = r"\$="
t_SUBSTRINGMATCH = r"\*="
t_IDENT = ident


@lex.TOKEN(string)
def t_STRING(t):
    t.value = t.value[1:-1]
    return t

t_FUNCTION = ident + r"\("
t_NUMBER = num
t_HASH = r"\#" + name
t_PLUS = w + r"\+"
t_GREATER = w + r">"
t_COMMA = w + r","
t_TILDE = w + r"~"
t_NOT = r":not\("
t_ATKEYWORD = r"@" + ident
t_INVALID = invalid
t_PERCENTAGE = num + r"%"
t_DIMENSION = num + ident
t_CDO = r"<!--"
t_CDC = r"-->"


# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)


lexer = lex.lex()


# %%


# \/\*[^*]*\*+([^/*][^*]*\*+)*\/                    /* ignore comments */
