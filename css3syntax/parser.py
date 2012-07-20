from tokenizer import tokenize


TOP_LEVEL_MODE = 1
AT_RULE_MODE = 2
RULE_MODE = 3
SELECTOR_MODE = 4
DECLARATION_MODE = 5
AFTER_DECLARATION_NAME_MODE = 6
DECLARATION_VALUE_MODE = 7
DECLARATION_END_MODE = 8
NEXT_BLOCK_ERROR_MODE = 9
NEXT_DECLARATION_ERROR_MODE = 10


class Stylesheet:
    
    content_mode = TOP_LEVEL_MODE
    
    def __init__(self):
        self.value = []
    
    def pretty_print(self):
        print "Stylesheet:"
        for item in self.value:
            item.pretty_print(1)


class AtRule:
    def __init__(self, name):
        self.name = name
        self.prelude = []
        self.value = []
    
    @property
    def content_mode(self):
        if self.name in ["media"]:  # rule-filled
            return RULE_MODE
        elif self.name in ["page"]:  # declaration-filled
            return DECLARATION_MODE
        else:
            xxx
    
    def pretty_print(self, indent):
        i = "  " * indent
        print i, "AtRule:"
        print i, "  Name:", self.name
        print i, "  Prelude:"
        for item in self.prelude:
            item.pretty_print(indent + 2)
        print i, "  Value:"
        for item in self.value:
            item.pretty_print(indent + 2)


class StyleRule:
    
    content_mode = DECLARATION_MODE
    
    def __init__(self):
        self.selector = []
        self.value = []
    
    def pretty_print(self, indent):
        i = "  " * indent
        print i, "StyleRule:"
        print i, "  Selector:"
        for item in self.selector:
            item.pretty_print(indent + 2)
        print i, "  Value:"
        for item in self.value:
            item.pretty_print(indent + 2)


class Declaration:
    def __init__(self, name):
        self.name = name
        self.value = []
    
    def pretty_print(self, indent):
        i = "  " * indent
        print i, "Declaration:"
        print i, "  Name:", self.name
        print i, "  Value:"
        for item in self.value:
            item.pretty_print(indent + 2)


class Primitive:
    def __init__(self, primitive):
        self.primitive = primitive
    
    def pretty_print(self, indent):
        i = "  " * indent
        print i, self.primitive


class Function:
    def __init__(self, name):
        self.name = name
        self.arguments = []
    
    def pretty_print(self, indent):
        i = "  " * indent
        print i, "Function:"
        print i, "  Name:", self.name
        print i, "  Arguments:"
        for argument in self.arguments:
            print i, "  -"
            for item in argument:
                item.pretty_print(indent + 2)


# NOTE: the goal of this parser is not to be elegant or fast but rather to
# follow the spec as much as possible

class Parser:
    
    def __init__(self, tokens):
        self.index = 0
        self.tokens = tokens
        self.mode = TOP_LEVEL_MODE
        self.open_rule_stack = [Stylesheet()]
    
    def consume_next_input_token(self):
        token = self.tokens[self.index]
        self.index += 1
        return token
    
    def reprocess_current_input_token(self):
        self.index -= 1
    
    def current_rule(self):
        return self.open_rule_stack[-1]
    
    def parse(self):
        while self.index < len(self.tokens):
            if self.mode == TOP_LEVEL_MODE:
                self.top_level_mode()
            elif self.mode == AT_RULE_MODE:
                self.at_rule_mode()
            elif self.mode == RULE_MODE:
                self.rule_mode()
            elif self.mode == SELECTOR_MODE:
                self.selector_mode()
            elif self.mode == DECLARATION_MODE:
                self.declaration_mode()
            elif self.mode == AFTER_DECLARATION_NAME_MODE:
                self.after_declaration_name_mode()
            elif self.mode == DECLARATION_VALUE_MODE:
                self.declaration_value_mode()
            else:
                print "UNKNOWN MODE", self.mode
                break
    
    def top_level_mode(self):
        token = self.consume_next_input_token()
        
        if token[0] == "cdo" or token[0] == "cdc" or token[0] == "whitespace":
            pass
        elif token[0] == "at":
            self.open_rule_stack.append(AtRule(name=token[1]))
            self.mode = AT_RULE_MODE
        elif token[0] == "{":
            # @@@ parse error
            self.consume_primitive(token)
        elif token[0] == "EOF":
            self.finish_parsing()
        else:
            self.open_rule_stack.append(StyleRule())
            self.mode = SELECTOR_MODE
            self.reprocess_current_input_token()
    
    def at_rule_mode(self):
        token = self.consume_next_input_token()
        
        if token[0] == ";":
            self.pop_current_rule()
            self.switch_to_current_rule_content_mode()
        elif token[0] == "{":
            if self.current_rule().name in ["media"]:  # rule-filled
                self.mode = RULE_MODE
            elif self.current_rule().name in ["page"]:  # declaration-filled
                self.mode = DECLARATION_MODE
            else:
                # @@@ parse error
                xxx
        elif token[0] == "EOF":
            xxx
        else:
            self.current_rule().prelude.append(self.consume_primitive(token))
    
    def rule_mode(self):
        token = self.consume_next_input_token()
        
        if token[0] == "whitespace":
            pass
        elif token[0] == "}":
            self.pop_current_rule()
            self.switch_to_current_rule_content_mode()
        elif token[0] == "at":
            xxx
        elif token[0] == "EOF":
            xxx
        else:
            self.open_rule_stack.append(StyleRule())
            self.mode = SELECTOR_MODE
            self.reprocess_current_input_token()
        
    def selector_mode(self):
        token = self.consume_next_input_token()
        
        if token[0] == "{":
            self.mode = DECLARATION_MODE
        elif token[0] == "EOF":
            # discard current rule
            self.finish_parsing()
        else:
            self.current_rule().selector.append(self.consume_primitive(token))
    
    def declaration_mode(self):
        token = self.consume_next_input_token()
        
        if token[0] == "whitespace" or token[0] == ";":
            pass
        elif token[0] == "}":
            self.pop_current_rule()
            self.switch_to_current_rule_content_mode
        elif token[0] == "at_rule":
            xxx
        elif token[0] == "identifier":
            self.current_declaration = Declaration(name=token[1])
            self.mode = AFTER_DECLARATION_NAME_MODE
        elif token[0] == "EOF":
            self.finish_parsing()
        else:
            # @@@ parse error
            self.current_declaration = None
            self.mode = NEXT_DECLARATION_ERROR_MODE
    
    def after_declaration_name_mode(self):
        token = self.consume_next_input_token()
        
        if token[0] == "whitespace":
            pass
        elif token[0] == "colon":
            self.mode = DECLARATION_VALUE_MODE
        elif token[0] == ";":
            # @@@ parse error
            self.current_declaration = None
            self.switch_to_current_rule_content_mode()
        elif token[0] == "EOF":
            self.current_declaration = None
            self.finish_parsing()
        else:
            # @@@ parse error
            self.current_declaration = None
            self.mode = NEXT_DECLARATION_ERROR_MODE
    
    def declaration_value_mode(self):
        token = self.consume_next_input_token()
        
        if token == ("delim", "!"):
            xxx
        elif token[0] == ";":
            # @@@ if grammatically valid
            self.current_rule().value.append(self.current_declaration)
            self.switch_to_current_rule_content_mode()
        elif token[0] == "}":
            # @@@ if grammatically valid
            self.current_rule().value.append(self.current_declaration)
            self.pop_current_rule()
            self.switch_to_current_rule_content_mode()
        elif token[0] == "EOF":
            self.finish_parsing()
        else:
            self.current_declaration.value.append(self.consume_primitive(token))
    
    def consume_primitive(self, token):
        if token[0] == "{" or token[0] == "[" or token == "(":
            return self.consume_simple_block(token)
        elif token[0] == "function":
            return self.consume_function(token)
        else:
            return Primitive(token)
    
    def consume_function(self, token):
        function = Function(token[1])
        current_argument = []
        while True:
            token = self.consume_next_input_token()
            if token[0] == "EOF" or token[0] == ")":
                function.arguments.append(current_argument)
                return function
            elif token == ("delim", ","):
                function.arguments.append(current_argument)
                current_argument = []
            else:
                current_argument.append(self.consume_primitive(token))
    
    def switch_to_current_rule_content_mode(self):
        self.mode = self.current_rule().content_mode
    
    def pop_current_rule(self):
        rule = self.open_rule_stack.pop()
        self.current_rule().value.append(rule)
