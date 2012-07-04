#!/usr/bin/env python

from selectors import ElementSelector, AttributeSelector


class Element:
    def __init__(self, name, attrs=None, children=None):
        self.parent = None
        self.name = name
        self.attrs = attrs or {}
        self.children = children or []
        for child in self.children:
            child.parent = self
    
    @property
    def prev(self):
        if self.parent is None:
            return None
        me = self.parent.children.index(self)
        
        if me == 0:
            return None
        
        return self.parent.children[me - 1]


class Text:
    def __init__(self, cdata):
        self.cdata = cdata


def selects(selector, element):
    return selector.selects(element)


## 6.1 type selector

assert selects(ElementSelector("E"), Element("E"))
assert not selects(ElementSelector("E"), Element("F"))


## 6.2 universal selector

assert selects(ElementSelector(), Element("E"))


## 6.3 attribute selectors

assert selects(AttributeSelector("att"), Element("E", {"att": "val"}))
assert not selects(AttributeSelector("att"), Element("E", {}))

assert selects(AttributeSelector("att", "val"), Element("E", {"att": "val"}))
assert not selects(AttributeSelector("att", "val"), Element("E", {"att": "other"}))
assert not selects(AttributeSelector("att", "val"), Element("E", {}))
assert selects(ElementSelector("h1").attr("title"), Element("h1", {"title": "The Title"}))
assert not selects(ElementSelector("h1").attr("title"), Element("h1"))
assert not selects(ElementSelector("h1").attr("title"), Element("h2", {"title": "The Title"}))
assert selects(ElementSelector("span").attr("hello", "Cleveland").attr("goodbye", "Columbus"), Element("span", {"hello": "Cleveland", "goodbye": "Columbus"}))

assert not selects(ElementSelector("a").attr("rel", "copyright"), Element("a", {"rel": "copyright copyleft"}))
assert selects(ElementSelector("a").attr("rel", "copyright", "~="), Element("a", {"rel": "copyright copyleft"}))
assert selects(ElementSelector("a").attr("hreflang", "en", "="), Element("a", {"hreflang": "en"}))
assert not selects(ElementSelector("a").attr("hreflang", "en", "="), Element("a", {"hreflang": "en-US"}))
assert selects(ElementSelector("a").attr("hreflang", "en", "|="), Element("a", {"hreflang": "en"}))
assert selects(ElementSelector("a").attr("hreflang", "en", "|="), Element("a", {"hreflang": "en-US"}))

assert selects(ElementSelector("object").attr("type", "image/", "^="), Element("object", {"type": "image/jpeg"}))
assert not selects(ElementSelector("object").attr("type", "image/"), Element("object", {"type": "image/jpeg"}))
assert selects(ElementSelector("a").attr("href", ".html", "$="), Element("a", {"href": "foo.html"}))
assert not selects(ElementSelector("a").attr("href", ".html"), Element("a", {"href": "foo.html"}))
assert selects(ElementSelector("p").attr("title", "hello", "*="), Element("p", {"title": "it's hello world"}))
assert not selects(ElementSelector("p").attr("title", "hello"), Element("p", {"title": "it's hello world"}))


## 8. Combinators

em = Element("em", {}, [Text("very")])
doc = Element("h1", {}, [
        Text("This "),
        Element("span", {"class": "myclass"}, [
            Text("headline is "), em, Text(" important")
        ])
    ])

assert selects(ElementSelector("h1").descendant(ElementSelector("em")), em)
assert not selects(ElementSelector("h2").descendant(ElementSelector("em")), em)
assert selects(ElementSelector("span").child(ElementSelector("em")), em)
assert not selects(ElementSelector("h1").child(ElementSelector("em")), em)

assert not selects(ElementSelector("h1").child(ElementSelector("em")), Element("em"))

sel = ElementSelector("div").descendant(ElementSelector("div")).descendant(ElementSelector("p"))
p = Element("p")
doc = Element("div", {}, [Element("div", {}, [p])])

assert selects(sel, p)

p = Element("p")
doc = Element("body", {}, [Element("div", {}, [p])])

assert not selects(sel, p)

sel1 = ElementSelector("body").descendant(ElementSelector()).descendant(ElementSelector("p"))
sel2 = ElementSelector("body").descendant(ElementSelector("p"))
p = Element("p")
doc = Element("body", {}, [p])
assert not selects(sel1, p)
assert selects(sel2, p)

sel = ElementSelector("div").descendant(ElementSelector("p")).descendant(ElementSelector().attr("href"))
a = Element("a", {"href": "http://example.com"})
doc = Element("div", {}, [Element("p", {}, [a])])
assert selects(sel, a)

# @@@ sibling combinators
p1 = Element("p")
p2 = Element("p")
math = Element("math")
doc1 = Element("div", {}, [math, p1])
doc2 = Element("div", {}, [Element("ul"), p2])
assert selects(ElementSelector("math").followed_by(ElementSelector("p")), p1)
assert not selects(ElementSelector("math").followed_by(ElementSelector("p")), p2)
assert not selects(ElementSelector("foo").followed_by(ElementSelector("math")), math)
assert not selects(ElementSelector("foo").followed_by(ElementSelector("div")), doc1)

print("all tests passed.")
