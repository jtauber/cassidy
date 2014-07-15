def previous_element(element):
    siblings = element.parent.childNodes

    if siblings.index(element) == 0:
        return None
    else:
        return siblings[siblings.index(element) - 1]


class ElementSelector:

    def __init__(self, name=None):
        self.name = name
        self.attr_selectors = []
        self.ancestor = None
        self.parent = None
        self.prev = None

    def __eq__(self, other):
        if (
            isinstance(other, ElementSelector) and
            self.name == other.name and
            self.attr_selectors == other.attr_selectors and
            self.ancestor == other.ancestor and
            self.parent == other.parent
        ):
            return True
        else:
            return False

    def append(self, attr_selector):
        self.attr_selectors.append(attr_selector)
        return self

    def attr(self, name, value=None, match_type="="):
        self.attr_selectors.append(AttributeSelector(name, value, match_type))
        return self

    def descendant(self, selector):
        selector.ancestor = self
        return selector

    def child(self, selector):
        selector.parent = self
        return selector

    def followed_by(self, selector):
        selector.prev = self
        return selector

    def this_select(self, element):
        if self.name is None:
            return True
        elif self.name == element.name:
            return True
        else:
            return False

    def ancestor_select(self, element):
        if element.parent is None:
            return False
        else:
            if self.ancestor.selects(element.parent):
                return True
            else:
                return self.ancestor_select(element.parent)

        # @@@ need to implement backtracking

    def parent_select(self, element):
        if element.parent is None:
            return False
        else:
            if self.parent.this_select(element.parent):
                return True
            else:
                return False

    def prev_select(self, element):
        prev = previous_element(element)

        if prev is None:
            return False
        else:
            if self.prev.this_select(prev):
                return True
            else:
                return False

    def selects(self, element):
        if not self.this_select(element):
            return False
        if not all(s.selects(element) for s in self.attr_selectors):
            return False
        if self.ancestor and not self.ancestor_select(element):
            return False
        if self.parent and not self.parent_select(element):
            return False
        if self.prev and not self.prev_select(element):
            return False

        return True

    def find(self, node):
        if self.selects(node):
            yield node
        for child in node.childNodes:
            for match in self.find(child):
                yield match


class AttributeSelector:
    def __init__(self, name, value=None, match_type="="):
        self.name = name
        self.value = value
        self.match_type = match_type

    def __eq__(self, other):
        if (
            isinstance(other, AttributeSelector) and
            self.name == other.name and
            self.value == other.value and
            self.match_type == other.match_type
        ):
            return True
        else:
            return False

    def selects(self, node):
        # silly check if node is an element
        if not hasattr(node, "attributes"):
            return False

        if self.value is None:
            if self.name in node.attributes:
                return True
        else:
            v = node.attributes.get(self.name)
            if v is None:
                return False
            if self.match_type == "=" and v == self.value:
                return True
            if self.match_type == "~=" and self.value in v.split():
                return True
            if self.match_type == "|=" and (v == self.value or v.startswith(self.value + "-")):
                return True
            if self.match_type == "^=" and v.startswith(self.value):
                return True
            if self.match_type == "$=" and v.endswith(self.value):
                return True
            if self.match_type == "*=" and self.value in v:
                return True
            return False

    def find(self, node):
        if self.selects(node):
            yield node
        for child in node.childNodes:
            for match in self.find(child):
                yield match
