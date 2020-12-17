import os
import json
import logging
import subprocess
import xml.etree.ElementTree as ElementTree
import xml.dom.minidom as minidom
from datetime import datetime, timezone

from .proc_xml import xml_to_map, proc_var, proc_elem

logger = logging.getLogger("aurore.api")

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
       if isinstance(obj, set):
          return list(obj)
       return json.JSONEncoder.default(self, obj)


def feed_init(args, config)->dict:
    pass

#--------------------------------------------
# Post
#--------------------------------------------
def post_init(args, config)->dict:
    if "type" in args: args.base = args.type.split("/")[0]
    print(args.base)
    lids = [k for k in config.namespace].sort()
    if lids:
        _, num = lids[-1].split("-")
        lid = f"{(int(num) + 1):04}"
    else:
        lid = f"{args.base}-0001"
    with open(config.init_type[args.type], "r") as f:
        lines = f.readlines()

    for i, ln in enumerate(lines): 
        lines[i] = ln.replace("$$lid",lid)
        lines[i] = ln.replace("$$published",datetime.now(timezone.utc).astimezone().isoformat())
    accum =  {
        "lid": lid,
        "base": ElementTree.fromstringlist(lines),
        "lines": [line for line in lines if "<input" not in line]
    }
    return accum

def post_close(args, config, accum):
    data = {}
    for i, ipt in enumerate(accum["base"].findall("input")):
        val = input(ipt.attrib["key"]+": ")
        try: 
            val = eval(val)
        except:
            pass
        data[ipt.attrib["key"]] = val

    if "$$lid" in args.location:
        destination = args.location.replace("$$lid",accum["lid"])
        os.mkdir(accum["lid"])
    else:
        destination = args.location
    with open(destination,"w+") as f:
        f.writelines(build_template(accum["lines"], data))
 
def build_template(template:list, data:dict):
    for k,v in data.items():
        for j,ln in enumerate(template):
            template[j] = ln.replace(k, str(v))
    return template

#--------------------------------------------
# Get
#--------------------------------------------
def get_init(args,config):

    accum = {"items": {}, "categories": {}}
    accum["categories"] = {
        scheme.attrib["key"]: {
            "map": xml_to_map(scheme.find("map")),
            "var": scheme.find("var")
        } for scheme in args.category_schemes
    }
    return accum

def get_item(rsrc, args:object, config:object, accum:dict)->dict:
    raw_item = xml_to_map(rsrc, args.base_uri)
    if "base" in rsrc.attrib:
        base = rsrc.attrib["base"]
    else:
        base = args.base_uri
    item = categorize(accum["categories"], raw_item, base)
    accum['items'].update({rsrc.attrib["id"]: item})
    return accum

def get_close(args, config, accum):
    output = {
        "items":  accum["items"]
    }
    if accum["categories"]:
        output.update({
            "categories": {
                category: accum["categories"][category]["map"] for category in accum["categories"]
            }
        })

    print(json.dumps(output,indent=2,cls=SetEncoder))


def categorize(categories, map_item, base_uri):
    map_item["categories"] = {}

    for category in categories:
        logger.info(f"Category base uri: {base_uri}")
        val = proc_elem(categories[category]["var"], base_uri, {"item": map_item})[0]
        if val is None: val="None"
        logger.info(f"Category value: {val}")
        assert val in categories[category]["map"], f"Key {val} not in mapping {categories[category]['map']}"
        map_item["categories"].update(
            {category: val}
            )

    return map_item
