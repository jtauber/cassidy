#!/usr/bin/env python

import html5lib

from selectors_parse import parser


def html(s):
    return html5lib.parse(s).childNodes[0].childNodes[1].childNodes[0]

def selector(s):
    return parser.parse(s)

## 6.1 type selector

assert selector("e").selects(html("<e>"))
assert not selector("e").selects(html("<f>"))


## 6.2 universal selector

assert selector("*").selects(html("<e>"))


## 6.3 attribute selectors

assert selector("[att]").selects(html("<e att='val'>"))
assert not selector("[att]").selects(html("<e>"))

assert selector("[att='val']").selects(html("<e att='val'>"))
assert not selector("[att='val']").selects(html("<e att='other'>"))
assert not selector("[att='val']").selects(html("<e>"))
assert selector("h1[title]").selects(html("<h1 title='The Title'>"))
assert not selector("h1[title]").selects(html("<h1>"))
assert not selector("h1[title]").selects(html("<h2 title='The Title'>"))
assert selector("span[hello='Cleveland'][goodbye='Columbus']").selects(html("<span hello='Cleveland' goodbye='Columbus'>"))

assert not selector("a[rel='copyright']").selects(html("<a rel='copyright copyleft'>"))
assert selector("a[rel~='copyright']").selects(html("<a rel='copyright copyleft'>"))
assert selector("a[hreflang='en']").selects(html("<a hreflang='en'>"))
assert not selector("a[hreflang='en']").selects(html("<a hreflang='en-US'>"))
assert selector("a[hreflang|='en']").selects(html("<a hreflang='en'>"))
assert selector("a[hreflang|='en']").selects(html("<a hreflang='en-US'>"))

assert selector("object[type^='image/']").selects(html("<object type='image/jpeg'>"))
assert not selector("object[type='image/']").selects(html("<object type='image/jpeg'>"))
assert selector("a[href$='.html']").selects(html("<a href='foo.html'>"))
assert not selector("a[href='.html']").selects(html("<a href='foo.html'>"))
assert selector("p[title*='hello']").selects(html('<p title="it\'s hello world">'))
assert not selector("p[title='hello']").selects(html('<p title="it\'s hello world">'))


## 8. Combinators

doc = html("""<h1>This <span class="myclass">headline is <em>very</em> important</span></h1>""")

em = doc.childNodes[1].childNodes[1]

assert selector("h1 em").selects(em)
assert not selector("h2 em").selects(em)
assert selector("span > em").selects(em)
assert not selector("h1 > em").selects(em)

assert not selector("h1 > em").selects(html("<em>"))

sel = selector("div * p")

doc = html("<div><div><p></div></div>")

p = doc.childNodes[0].childNodes[0]

assert sel.selects(p)

doc = html("<section><div><p></div></section>")

p = doc.childNodes[0].childNodes[0]

assert not sel.selects(p)

sel1 = selector("body * p")
sel2 = selector("body p")

p = html("<body><p></body>")

assert not sel1.selects(p)
assert sel2.selects(p)

sel = selector("div p *[href]")

doc = html("""<div><p><a href="http://example.com">example</a></p></div>""")

a = doc.childNodes[0].childNodes[0]

assert sel.selects(a)

doc1 = html("<div><math/><p>test</p></div>")
math = doc1.childNodes[0]
p1 = doc1.childNodes[1]

doc2 = html("<div><ul></ul><p>test</p></div>")
p2 = doc2.childNodes[1]

assert selector("math + p").selects(p1)
assert not selector("math + p").selects(p2)
assert not selector("foo + math").selects(math)
assert not selector("foo + div").selects(doc1)

print("all tests passed.")
