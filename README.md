Cassidy
=======

The beginnings of a CSS library for Python.

At present it implements a decent part of the CSS Selectors spec and the
draft CSS3-Syntax spec.

Here's an example of the selectors implementation:

    >>> import html5lib
    >>> from cassidy.selectors import selector
    >>> doc = html5lib.parse("<div><p id='foo'>hello</p><p class='bar'>world</p></div>")
    >>> for element in selector("p").find(doc):
    ...     print element.toxml()
    ... 
    <p id="foo">hello</p>
    <p class="bar">world</p>
    
    >>> for element in selector("div .bar").find(doc):
    ...     print element.toxml()
    ... 
    <p class="bar">world</p>

The `css3syntax` directory is a work-in-progress implementation of CSS3-Syntax
draft spec. `css3_selectors_test.py` is a test-driven implementation of selectors
using `css3syntax` for tokenization and parsing rather than PLY as
`cassidy.selectors` does. The same actual selector implementation is used, though.
This version will likely replace the PLY-based version eventually.

Besides improving all the above, the plan next is to implement the property model
and then value calculation and inheritance.
