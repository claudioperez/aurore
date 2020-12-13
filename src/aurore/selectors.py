import re
import fnmatch
import logging
import jsonpointer

logger = logging.getLogger("aurore.selectors")

def iterate_leaves(item):
    if isinstance(item,(str,float,int)):
        yield item
    elif isinstance(item,dict):
        for leaf in item.values():
            yield from iterate_leaves(leaf)
    elif isinstance(item,(tuple,list)):
        for leaf in item:
            yield from iterate_leaves(leaf)


class Pattern:
    def __init__(self, pattern):
        self.pattern = pattern

    def validate(self,field)->bool:
        if isinstance(field,(str,float,int)):
            logger.debug(f"{self.pattern}, {field}")
            return fnmatch.fnmatch(field,self.pattern)
        else:
            return self.pattern == field


class Pointer:
    token_keys = {
        "c": lambda i,_: i["categories"],
        "t": lambda i,_: i["title"],
        "i": lambda i,_: i["id"],
    }

    def __init__(self, pointer:str,recurse=False):
        self.recurse = recurse
        if pointer[0] == "%":
            self.tokens = re.split("([%|/][^/]*)", pointer)[1::2]
        else:
            raise Exception("Unimplemented pattern handler.")
    
    def resolve_tokens(self,item):
        for token in self.tokens:
            if re.match("^%.*", token):
                item = Pointer.token_keys[token[1]](item,None)
            elif re.match("^/.*",token):
                item = jsonpointer.resolve_pointer(item, token)
        return item

    def resolve(self,item):
        base = self.resolve_tokens(item)
        return base

    def resolve_recursively(self,item):
        base = self.resolve_tokens(item)
        for i in iterate_leaves(base):
            yield i


class Selector:
    def __init__(self,selector:str):

        if ":" in selector:
            recurse = True
            pointer, pattern = selector.split(":")
        elif "=" in selector:
            recurse = False
            pointer, pattern = selector.split("=")
        else:
            recurse = False
            pointer, pattern = "/id", selector


        self.pattern = Pattern(pattern)
        self.pointer = Pointer(pointer,recurse=recurse)
        self.recurse = recurse


    def validate(self,item):
        if self.recurse:
            return any(
                self.pattern.validate(val) for val in self.pointer.resolve_recursively(item)
            )
        else:
            return self.pattern.validate(self.pointer.resolve(item))


def check_includes(args, item):
    logger.debug(args.include_item)
    if "include_item" in args and args.include_item:
        selectors = [Selector(i) for i in args.include_item]
        return any(selector.validate(item) for selector in selectors)
    else:
        return True

