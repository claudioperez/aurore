from typing import Callable
from argparse import Namespace

import yaml
# from anabel import interface 
interface = lambda x: x

class Config:
    def __init__(self,filename="~/.local/share/aurore/aurore.yaml"):
        with open(filename) as f:
            config  = yaml.load(f, Loader=yaml.Loader)
        self.namespace = config["namespace"]

        if "base-uri" in config:
            self.base_uri = config["base-uri"]
        else:
            self.base_uri = ""

        if "field-filter" in config:
            self.field_filter = config["field_filter"]
        else:
            self.field_filter = []


@interface 
class InitOperation:
    args: Namespace

@interface 
class ItemOperation:
    args: Namespace

@interface 
class EndOperation:
    accum: Callable
    args: Namespace
    config: Config