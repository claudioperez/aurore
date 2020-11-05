from typing import Callable
from argparse import Namespace

# from anabel import interface 
interface = lambda x: x

class Config: pass


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