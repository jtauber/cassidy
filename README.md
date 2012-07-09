Cassidy
=======

The beginnings of a CSS library for Python.

At present it implements a decent part of the CSS selectors spec.

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

Next is to implement the property model and then value calculation and inheritance.
