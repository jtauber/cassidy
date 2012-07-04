#!/usr/bin/env python

import html5lib

from selectors import ElementSelector, AttributeSelector


def html(s):
    return html5lib.parse(s).childNodes[0].childNodes[1].childNodes[0]


## 6.1 type selector

assert ElementSelector("e").selects(html("<e>"))
assert not ElementSelector("e").selects(html("<f>"))


## 6.2 universal selector

assert ElementSelector().selects(html("<e>"))


## 6.3 attribute selectors

assert AttributeSelector("att").selects(html("<e att='val'>"))
assert not AttributeSelector("att").selects(html("<e>"))

assert AttributeSelector("att", "val").selects(html("<e att='val'>"))
assert not AttributeSelector("att", "val").selects(html("<e att='other'>"))
assert not AttributeSelector("att", "val").selects(html("<e>"))
assert ElementSelector("h1").attr("title").selects(html("<h1 title='The Title'>"))
assert not ElementSelector("h1").attr("title").selects(html("<h1>"))
assert not ElementSelector("h1").attr("title").selects(html("<h2 title='The Title'>"))
assert ElementSelector("span").attr("hello", "Cleveland").attr("goodbye", "Columbus").selects(html("<span hello='Cleveland' goodbye='Columbus'>"))

assert not ElementSelector("a").attr("rel", "copyright").selects(html("<a rel='copyright copyleft'>"))
assert ElementSelector("a").attr("rel", "copyright", "~=").selects(html("<a rel='copyright copyleft'>"))
assert ElementSelector("a").attr("hreflang", "en", "=").selects(html("<a hreflang='en'>"))
assert not ElementSelector("a").attr("hreflang", "en", "=").selects(html("<a hreflang='en-US'>"))
assert ElementSelector("a").attr("hreflang", "en", "|=").selects(html("<a hreflang='en'>"))
assert ElementSelector("a").attr("hreflang", "en", "|=").selects(html("<a hreflang='en-US'>"))

assert ElementSelector("object").attr("type", "image/", "^=").selects(html("<object type='image/jpeg'>"))
assert not ElementSelector("object").attr("type", "image/").selects(html("<object type='image/jpeg'>"))
assert ElementSelector("a").attr("href", ".html", "$=").selects(html("<a href='foo.html'>"))
assert not ElementSelector("a").attr("href", ".html").selects(html("<a href='foo.html'>"))
assert ElementSelector("p").attr("title", "hello", "*=").selects(html('<p title="it\'s hello world">'))
assert not ElementSelector("p").attr("title", "hello").selects(html('<p title="it\'s hello world">'))


## 8. Combinators

doc = html("""<h1>This <span class="myclass">headline is <em>very</em> important</span></h1>""")

em = doc.childNodes[1].childNodes[1]

assert ElementSelector("h1").descendant(ElementSelector("em")).selects(em)
assert not ElementSelector("h2").descendant(ElementSelector("em")).selects(em)
assert ElementSelector("span").child(ElementSelector("em")).selects(em)
assert not ElementSelector("h1").child(ElementSelector("em")).selects(em)

assert not ElementSelector("h1").child(ElementSelector("em")).selects(html("<em>"))

sel = ElementSelector("div").descendant(ElementSelector("div")).descendant(ElementSelector("p"))

doc = html("<div><div><p></div></div>")

p = doc.childNodes[0].childNodes[0]

assert sel.selects(p)

doc = html("<section><div><p></div></section>")

p = doc.childNodes[0].childNodes[0]

assert not sel.selects(p)

sel1 = ElementSelector("body").descendant(ElementSelector()).descendant(ElementSelector("p"))
sel2 = ElementSelector("body").descendant(ElementSelector("p"))

p = html("<body><p></body>")

assert not sel1.selects(p)
assert sel2.selects(p)

sel = ElementSelector("div").descendant(ElementSelector("p")).descendant(ElementSelector().attr("href"))

doc = html("""<div><p><a href="http://example.com">example</a></p></div>""")

a = doc.childNodes[0].childNodes[0]

assert sel.selects(a)

doc1 = html("<div><math/><p>test</p></div>")
math = doc1.childNodes[0]
p1 = doc1.childNodes[1]

doc2 = html("<div><ul></ul><p>test</p></div>")
p2 = doc2.childNodes[1]

assert ElementSelector("math").followed_by(ElementSelector("p")).selects(p1)
assert not ElementSelector("math").followed_by(ElementSelector("p")).selects(p2)
assert not ElementSelector("foo").followed_by(ElementSelector("math")).selects(math)
assert not ElementSelector("foo").followed_by(ElementSelector("div")).selects(doc1)

print("all tests passed.")
