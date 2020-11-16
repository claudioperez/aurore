import os
import json
from functools import reduce

import yaml
import jinja2
import elstir.utils.filters as elstir_filters

from aurore.utils import get_resource_location

def init(args, config)-> dict:
    with open(args.template_data,"r") as f:
        template_data = yaml.load(f,Loader=yaml.Loader)
    return {
        "items": [],
        "template_data": template_data,
        "filter_values": {}
    }

def item(rsrc, args, config, accum: dict)->dict: #card
    item_data = get_children(rsrc, config, accum["template_data"])
    accum["items"].append(item_data)
    return accum

def close(args, config, accum):
    # exec get filters
    filters = elstir_get_filters(accum["template_data"])
    filter_values = elstir_filters._get_gallery_filters(accum["items"])
    env = jinja2.Environment(
            loader=jinja2.PackageLoader("aurore","report/tmpl_0001")
            # autoescape=jinja2.select_autoescape(["html","xml"])
        )
    env.filters["tojson"] = lambda obj,**kwargs: jinja2.Markup(json.dumps(obj, **kwargs))
    template = env.get_template("main.html")
    page = template.render(
        filters=filters,
        filter_values=filter_values,
        items=accum["items"])
    print(page)

def get_children(rsrc:dict, config, data_fields:dict)->dict:
    path = get_resource_location(rsrc, config) + "/index"
    data = {
        "id": rsrc["id"],
        "title": rsrc["title"],
        "synopsis": rsrc["abstract"],
        "url": rsrc["id"] + "/README.html",
        "image": elstir_filters._get_dir_image(path),
        "template_data": elstir_filters.getParentTemplateFields(path,data_fields)
    }
    # print(data)
    return data
    
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