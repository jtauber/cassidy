from .selectors import ElementSelector, AttributeSelector

import ply.yacc as yacc

from .lexer import tokens  # noqa


def p_selectors_group(p):
    """
    selectors_group : selector
    """
    p[0] = p[1]


def p_selector(p):
    """
    selector : simple_selector_sequence
    """
    p[0] = p[1]


def p_selector_descendant(p):
    """
    selector : selector S simple_selector_sequence
    """
    p[0] = p[1].descendant(p[3])


def p_selector_child(p):
    """
    selector : selector GREATER simple_selector_sequence
    """
    p[0] = p[1].child(p[3])


def p_selector_followed_by(p):
    """
    selector : selector PLUS simple_selector_sequence
    """
    p[0] = p[1].followed_by(p[3])


def p_simple_selector_sequence1(p):
    """
    simple_selector_sequence : simple_selector
    """
    p[0] = p[1]


def p_simple_selector_sequence2(p):
    """
    simple_selector_sequence : repeatable_selector_sequence
    """
    p[0] = p[1][0]
    for extra in p[1][1:]:
        p[0].append(extra)


def p_simple_selector_sequence3(p):
    """
    simple_selector_sequence : simple_selector repeatable_selector_sequence
    """
    p[0] = p[1]
    for extra in p[2]:
        p[0].append(extra)


def p_repeatable_selector_sequence(p):
    """
    repeatable_selector_sequence : repeatable_selector
                                 | repeatable_selector repeatable_selector_sequence
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


def p_repeatable_selector(p):
    """
    repeatable_selector : hash_selector
                        | class_selector
                        | attribute_selector
    """
    p[0] = p[1]


def p_hash_selector(p):
    """
    hash_selector : HASH
    """
    p[0] = AttributeSelector("id", p[1][1:])


def p_class_selector(p):
    """
    class_selector : '.' IDENT
    """
    p[0] = AttributeSelector("class", p[2])


def p_attribute_selector1(p):
    """
    attribute_selector : '[' IDENT ']'
    """
    p[0] = AttributeSelector(p[2])


def p_attribute_selector2(p):
    """
    attribute_selector : '[' IDENT '=' STRING ']'
                       | '[' IDENT INCLUDES STRING ']'
                       | '[' IDENT DASHMATCH STRING ']'
                       | '[' IDENT PREFIXMATCH STRING ']'
                       | '[' IDENT SUFFIXMATCH STRING ']'
                       | '[' IDENT SUBSTRINGMATCH STRING ']'
    """
    p[0] = AttributeSelector(p[2], p[4], p[3])


def p_simple_selector(p):
    """
    simple_selector : type_selector
                    | universal
    """
    p[0] = p[1]


def p_type_selector(p):
    """
    type_selector : element_name
    """
    p[0] = ElementSelector(p[1])


def p_universal(p):
    """
    universal : '*'
    """
    p[0] = ElementSelector()


def p_element_name(p):
    """
    element_name : IDENT
    """
    p[0] = p[1]


parser = yacc.yacc()


if __name__ == "__main__":
    assert parser.parse("e") == ElementSelector("e")
    assert parser.parse("*") == ElementSelector()
    assert parser.parse("[att]") == AttributeSelector("att")
    assert parser.parse("*[att]") == ElementSelector().attr("att")
    assert parser.parse("*[att='val']") == ElementSelector().attr("att", "val")
    assert parser.parse("h1[title]") == ElementSelector("h1").attr("title")
    assert parser.parse("span[hello='Cleveland'][goodbye='Columbus']") == ElementSelector("span").attr("hello", "Cleveland").attr("goodbye", "Columbus")

    assert parser.parse("a[rel='copyright']") == ElementSelector("a").attr("rel", "copyright")
    assert parser.parse("a[rel~='copyright']") == ElementSelector("a").attr("rel", "copyright", "~=")
    assert parser.parse("a[hreflang='en']") == ElementSelector("a").attr("hreflang", "en", "=")
    assert parser.parse("a[hreflang|='en']") == ElementSelector("a").attr("hreflang", "en", "|=")
    assert parser.parse("object[type^='image/']") == ElementSelector("object").attr("type", "image/", "^=")
    assert parser.parse("object[type='image/']") == ElementSelector("object").attr("type", "image/")
    assert parser.parse("a[href$='.html']") == ElementSelector("a").attr("href", ".html", "$=")
    assert parser.parse("a[href='.html']") == ElementSelector("a").attr("href", ".html")
    assert parser.parse("p[title*='hello']") == ElementSelector("p").attr("title", "hello", "*=")
    assert parser.parse("p[title='hello']") == ElementSelector("p").attr("title", "hello")

    assert parser.parse("h1 em") == ElementSelector("h1").descendant(ElementSelector("em"))
    assert parser.parse("span > em") == ElementSelector("span").child(ElementSelector("em"))
    assert parser.parse("div * p") == ElementSelector("div").descendant(ElementSelector()).descendant(ElementSelector("p"))
    assert parser.parse("div p *[href]") == ElementSelector("div").descendant(ElementSelector("p")).descendant(ElementSelector().attr("href"))
    assert parser.parse("math + p") == ElementSelector("math").followed_by(ElementSelector("p"))
