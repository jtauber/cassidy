#!/usr/bin/env python

from cassidy.selectors.selectors import *
from css3syntax.tokenizer import Tokenizer
from css3syntax.parser import Parser, Primitive, SimpleBlock

# assert parser.parse("e") == ElementSelector("e")


TOP_LEVEL_MODE = 0
ELEMENT_MODE = 1
ATTRIBUTE_MODE = 2
CHILD_MODE = 3
FOLLOWED_BY_MODE = 4


class Selector:

    def __init__(self, s):
        p = Parser(list(Tokenizer(s + "{}").tokenize()))
        p.parse()
        self.primitives = p.open_rule_stack[0].value[0].selector
        self.index = 0
        self.mode = TOP_LEVEL_MODE
        self.current_selector = None

    def consume_next_primitive(self):
        primitive = self.primitives[self.index]
        self.index += 1
        if isinstance(primitive, Primitive) and primitive.primitive[0] == "whitespace":
            return self.consume_next_primitive()
        return primitive

    def reprocess_current_primitive(self):
        self.index -= 1

    def parse(self):
        while self.index < len(self.primitives):
            if self.mode == TOP_LEVEL_MODE:
                self.top_level_mode()
            elif self.mode == ELEMENT_MODE:
                self.element_mode()
            elif self.mode == ATTRIBUTE_MODE:
                self.attribute_mode()
            elif self.mode == CHILD_MODE:
                self.child_mode()
            elif self.mode == FOLLOWED_BY_MODE:
                self.followed_by_mode()
            else:
                print "UNKNOWN MODE", self.mode
                quit()

        return self.current_selector

    def top_level_mode(self):
        primitive = self.consume_next_primitive()

        if isinstance(primitive, Primitive):
            if primitive.primitive[0] == "identifier":
                self.current_selector = ElementSelector(primitive.primitive[1])
                self.mode = ELEMENT_MODE
            elif primitive.primitive == ("delim", "*"):
                self.current_selector = ElementSelector()
                self.mode = ELEMENT_MODE
            else:
                assert False
        elif isinstance(primitive, SimpleBlock):
            if primitive.associated_token == ("[",):
                self.reprocess_current_primitive()
                self.mode = ATTRIBUTE_MODE
            else:
                assert False
        else:
            assert False

    def element_mode(self):
        primitive = self.consume_next_primitive()

        if isinstance(primitive, SimpleBlock):
            if primitive.associated_token == ("[",):
                self.reprocess_current_primitive()
                self.mode = ATTRIBUTE_MODE
            else:
                assert False
        elif isinstance(primitive, Primitive):
            if primitive.primitive[0] == "identifier":
                self.current_selector = self.current_selector.descendant(ElementSelector(primitive.primitive[1]))
            elif primitive.primitive == ("delim", ">"):
                self.mode = CHILD_MODE
            elif primitive.primitive == ("delim", "*"):
                self.current_selector = self.current_selector.descendant(ElementSelector())
            elif primitive.primitive == ("delim", "+"):
                self.mode = FOLLOWED_BY_MODE
            else:
                assert False
        else:
            assert False

    def child_mode(self):
        primitive = self.consume_next_primitive()

        if isinstance(primitive, Primitive) and primitive.primitive[0] == "identifier":
            self.current_selector = self.current_selector.child(ElementSelector(primitive.primitive[1]))
        else:
            assert False

    def followed_by_mode(self):
        primitive = self.consume_next_primitive()

        if isinstance(primitive, Primitive) and primitive.primitive[0] == "identifier":
            self.current_selector = self.current_selector.followed_by(ElementSelector(primitive.primitive[1]))
        else:
            assert False

    def attribute_mode(self):
        block = self.consume_next_primitive()
        if len(block.value) == 1:
            if block.value[0].primitive[0] == "identifier":
                if self.current_selector:
                    attr_selector = AttributeSelector(block.value[0].primitive[1])
                    self.current_selector.append(attr_selector)
                else:
                    self.current_selector = AttributeSelector(block.value[0].primitive[1])
            else:
                assert False
        elif len(block.value) == 3:
            if (
                block.value[0].primitive[0] == "identifier" and
                block.value[1].primitive[0] == "delim" and
                block.value[2].primitive[0] == "string"
            ):
                attr_selector = AttributeSelector(
                    block.value[0].primitive[1],
                    block.value[2].primitive[1],
                    block.value[1].primitive[1])
                self.current_selector.append(attr_selector)
            else:
                assert False
        elif len(block.value) == 4:
            if (
                block.value[0].primitive[0] == "identifier" and
                block.value[1].primitive[0] == "delim" and
                block.value[2].primitive[0] == "delim" and
                block.value[3].primitive[0] == "string"
            ):
                attr_selector = AttributeSelector(
                    block.value[0].primitive[1],
                    block.value[3].primitive[1],
                    block.value[1].primitive[1] + block.value[2].primitive[1])
                self.current_selector.append(attr_selector)
            else:
                assert False
        else:
            assert False


assert Selector("e").parse() == ElementSelector("e")
assert Selector("*").parse() == ElementSelector()
assert Selector("[att]").parse() == AttributeSelector("att")
assert Selector("*[att]").parse() == ElementSelector().attr("att")
assert Selector("*[att='val']").parse() == ElementSelector().attr("att", "val")
assert Selector("h1[title]").parse() == ElementSelector("h1").attr("title")
assert Selector("span[hello='Cleveland'][goodbye='Columbus']").parse() == ElementSelector("span").attr("hello", "Cleveland").attr("goodbye", "Columbus")

assert Selector("a[rel='copyright']").parse() == ElementSelector("a").attr("rel", "copyright")
assert Selector("a[rel~='copyright']").parse() == ElementSelector("a").attr("rel", "copyright", "~=")
assert Selector("a[hreflang='en']").parse() == ElementSelector("a").attr("hreflang", "en", "=")
assert Selector("a[hreflang|='en']").parse() == ElementSelector("a").attr("hreflang", "en", "|=")
assert Selector("object[type^='image/']").parse() == ElementSelector("object").attr("type", "image/", "^=")
assert Selector("object[type='image/']").parse() == ElementSelector("object").attr("type", "image/")
assert Selector("a[href$='.html']").parse() == ElementSelector("a").attr("href", ".html", "$=")
assert Selector("a[href='.html']").parse() == ElementSelector("a").attr("href", ".html")
assert Selector("p[title*='hello']").parse() == ElementSelector("p").attr("title", "hello", "*=")
assert Selector("p[title='hello']").parse() == ElementSelector("p").attr("title", "hello")

assert Selector("h1 em").parse() == ElementSelector("h1").descendant(ElementSelector("em"))
assert Selector("span > em").parse() == ElementSelector("span").child(ElementSelector("em"))
assert Selector("div * p").parse() == ElementSelector("div").descendant(ElementSelector()).descendant(ElementSelector("p"))
assert Selector("div p *[href]").parse() == ElementSelector("div").descendant(ElementSelector("p")).descendant(ElementSelector().attr("href"))
assert Selector("math + p").parse() == ElementSelector("math").followed_by(ElementSelector("p"))

print("all tests passed.")
