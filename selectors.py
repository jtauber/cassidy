class ElementSelector:
    
    def __init__(self, name=None):
        self.name = name
        self.attr_selectors = []
        self.ancestor = None
        self.parent = None
        self.prev = None
    
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
        if element.prev is None:
            return False
        else:
            if self.prev.this_select(element.prev):
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


class AttributeSelector:
    def __init__(self, name, value=None, match_type="="):
        self.name = name
        self.value = value
        self.match_type = match_type
    
    def selects(self, element):
        if self.value is None:
            if self.name in element.attrs:
                return True
        else:
            v = element.attrs.get(self.name)
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
