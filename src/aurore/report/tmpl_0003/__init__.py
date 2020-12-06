import os
import json
from functools import reduce

import yaml
import jinja2
import elstir.utils.filters as elstir_filters

from aurore.utils import get_resource_location
from aurore.api import get_item

def init(args, config)-> dict:
    return {
        "items": [],
        "filter_values": {}
    }

item = get_item

def close(args, config, accum):
    # print(accum["items"])
    env = jinja2.Environment(
            loader=jinja2.PackageLoader("aurore","report/tmpl_0003")
        )
    env.filters["tojson"] = lambda obj,**kwargs: jinja2.Markup(json.dumps(obj, **kwargs))
    template = env.get_template("main.html")
    page = template.render(items=accum["items"])
    print(page)


    
def elstir_get_filters(template_data: dict)-> dict:
    # print(f"TEMP-DATA: {template_data}\n")
    if "filters" in template_data:
        gallery_items = template_data['gallery_items']
        filters = template_data['filters']
        # print(gallery_items,filters)
        args = [{k:v} for f in gallery_items.values() for k,v in f.items() if k in filters]
        return reduce(lambda x,y: {**x,**y},args)
    else:
        return {}
