from .parser import parser


def selector(s):
    return parser.parse(s)
