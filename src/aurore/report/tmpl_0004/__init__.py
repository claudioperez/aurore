import os
import json
from functools import reduce

import yaml
import jinja2

from aurore.utils import get_resource_location
from aurore.api import get_item

def init(args, config)-> dict:
    print_fields = []
    # for field in args.print:
    #     if ":" in field:
    #         elem,attrib = field.split(":")
    #         print_fields.append()

    return {
        "items": [],
        "print-attribs": [f for f in args.print if ":" in f],
        "print-text": [f for f in args.print if ":" not in f],
        "filter_values": {}
    }

item = get_item

def close(args, config, accum):
    # print(accum["print-attribs"])
    # print(accum["items"])
    env = jinja2.Environment(
            loader=jinja2.PackageLoader("aurore","report/tmpl_0004")
        )
    env.filters["tojson"] = lambda obj,**kwargs: jinja2.Markup(json.dumps(obj, **kwargs))
    template = env.get_template("main.html")
    page = template.render(
        items=accum["items"],
        text_fields=accum["print-text"],
        attrib_fields=accum["print-attribs"])
    print(page)


    