#!/usr/bin/env python


import os
import re
import argparse
import distutils, shutil, logging
from distutils import dir_util
import xml.etree.ElementTree as ElementTree
import urllib.parse
from pathlib import Path

import yaml

from .api import \
    post_init, post_close, \
    get_init, get_item, get_close
# from .core import InitOperation, ItemOperation
# from .report import init_report
from .uri_utils import resolve_uri
from aurore import config

logger = logging.getLogger(__name__)

try:
    import coloredlogs
    coloredlogs.install()
except:
    pass



def pass_item(item, args, config, accum:dict)->dict:
    return accum

def _apply_filter(rsrc:dict,filter:dict)->set:
    if "match" in filter:
        for key, pattern in filter["match"].items():
            if re.match(pattern,rsrc[key]):
                continue
            else:
                return False
    return set(filter["rules"]) if "rules" in filter else True

def apply_field_filters(resource:ElementTree,filters:dict)->bool:
    matches = []
    for field,fltrs in filters.items():
        j_matches = []
        if ":" in field:
            elem_name, attrib = field.split(":")
            for fltr in fltrs:
                fltr_j_matched = False
                for el in resource.findall(elem_name):
                    if fltr.search(el.attrib[attrib]):
                        fltr_j_matched = True
                        break
                j_matches.append(fltr_j_matched)
        matches.append(all(j_matches))
    return all(matches)


def main()->int:
    parser = argparse.ArgumentParser(prog='aurore', description="Description text.")
    # parser.add_argument("-C","--category-file",  nargs="?",  action="append")
    parser.add_argument("-D","--database-file",  nargs="?",  default=".aurore/aurore.db.xml")
    # parser.add_argument("-I","--include-item", nargs="?", action="append")
    # parser.add_argument("-E","--exclude",nargs="*", action="extend")
    parser.add_argument("-B","--base-uri", default="")
    parser.add_argument("-d","--defaults", nargs="?", action="append")
    parser.add_argument("-v","--verbose", action="count", default=0)
    parser.add_argument("-q","--quiet", action="store_true")

    subparsers = parser.add_subparsers(title='subcommands') #,description='list of subcommands',help='additional help')
    
    #-Post-------------------------------------------------------------
    post_parser = subparsers.add_parser("post", help="create new entity")
    post_parser.add_argument("type")
    post_parser.add_argument("location", nargs="?", default="$$lid/metadata.xml")
    post_parser.set_defaults(initfunc=post_init)
    post_parser.set_defaults(func=None)
    post_parser.set_defaults(closefunc=post_close)

    #-Get-------------------------------------------------------------
    get_parser = subparsers.add_parser("get", help="retrieve an entity")
    get_parser.add_argument("item-selectors", nargs="*", default=["*"])
    get_parser.set_defaults(initfunc=get_init)
    get_parser.set_defaults(func=get_item)
    get_parser.set_defaults(closefunc=get_close)


    #-----------------------------------------------------------------
    # Main
    #-----------------------------------------------------------------
    args = parser.parse_args()
    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=levels[args.verbose])
    if args.quiet: logger.setLevel(levels[0])

    #-Config----------------------------------------------------------
    cfg = config.load_config()

    #-Main-----------------------------------------------------------

    accum = {}
    if args.base_uri:
        pass
    else:
        args.base_uri = cfg["base_uri"]
    logger.info(f"args: {args}")

    # if args.database_file:
    #     database_file = args.database_file[0]
    
    tree = ElementTree.parse(args.database_file)
    root = tree.getroot()
    items = root.find("items")
    category_schemes = tree.findall(".//category-scheme")
    if not args.base_uri and "base" in items.attrib:
        args.base_uri = root.find("items").attrib["base"]
    
    if args.category_file:
        categories = ElementTree.parse(args.category_file[0])
        category_schemes.append(categories.findall("category-scheme"))

    setattr(args, "category_schemes", category_schemes)
    logger.info(f"category schemes: {category_schemes}")

    FILTERS = {}
    if args.exclude:
        for fltr in args.exclude:
            if ":" in fltr:
                field, pattern = fltr.rsplit(":",1)
            else:
                pattern = fltr 
                field = "item:id"

            if field in FILTERS:
                FILTERS[field].extend(re.compile(pattern))
            else:
                FILTERS.update({field: [re.compile(pattern)]})
    logger.info(f"filters: {FILTERS}")

    #-------------------------------------------------------------------
    if "initfunc" in args:
        accum = args.initfunc(args,cfg)
    else:
        accum = {}
    
    if args.func:
        for item in items:
            if "src" in item.attrib:
                resource_path = os.path.join(args.base_uri, item.attrib["src"])
                logger.info(f"Resource path: {resource_path}")
                resource = resolve_uri(resource_path)
            else:
                resource = item
            
            if apply_field_filters(resource,FILTERS):
                logger.info("Entering {}".format(item.attrib["id"]))
                logger.debug(f"Item: {item}")
                key = ElementTree.Element("str")
                key.attrib.update({"key": "id"})
                key.text = item.attrib["id"]
                resource.insert(0, key)
                accum = args.func(resource, args, cfg, accum)


    if "closefunc" in args:
        args.closefunc(args, cfg, accum)
    
    return 0

if __name__ == "__main__": main()
