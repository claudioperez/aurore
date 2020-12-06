#!/usr/bin/env python


import os, re, argparse, distutils, shutil, logging
import xml.etree.ElementTree as ElementTree
from distutils import dir_util
import urllib.parse
from pathlib import Path

import yaml
from oaks.lists import list_merge, test_item_by_key

from .api import \
    post_init, post_close, \
    get_init, get_item, get_close
from .core import Config, InitOperation, ItemOperation
from .report import init_report
from .utils import copy_tree, get_resource_location, isrepository
from .uri_utils import resolve_uri

logger = logging.getLogger(__name__)

try:
    import coloredlogs
    coloredlogs.install()
except:
    pass


class CopyConfig(Config): pass


def pass_item(item, args, config, accum:dict)->dict:
    return accum

def _append_gitignore(entry,destination_dir):
    gitignore = os.path.join(destination_dir,'.gitignore')
    if os.path.isfile(gitignore):
        with open(gitignore,'r') as f:
            items = set(f.readlines())
        logger.debug(f"adding \"{entry}\" to .gitignore")
        items.add(entry+'\n')
        with open(gitignore,'w+') as f:
            f.writelines(items)
    else:
        print(f"Creating .gitignore with entry {entry}")
        with open(gitignore,'w+') as f:
            f.write(entry+'\n')

def update_src_metadata(rsrc, args, config, accum=None):
    destination_dir = get_resource_location(rsrc,config)
    try:
        destination = os.path.join(destination_dir,args.metafile)
        with open(destination,'w+') as mf:
            logger.info(f"Copying {rsrc['id']} data to {destination}")
            mf.write(yaml.dump(rsrc))
    except Exception as e:
        logger.error(rsrc)
        logger.error(e)
        return

    if args.commit and "URL" in rsrc:
        if isrepository(rsrc["URL"]):
            gitdir = get_resource_location(rsrc,config)
            os.system(f"git -C {gitdir} pull")
            os.system(f"git -C {gitdir} add {args.metafile}")
            os.system(f"git -C {gitdir} commit -am 'Auto-update {args.metafile}'")
            os.system(f"git -C {gitdir} push")

def git_item(rsrc,args,config=None):
    if "URL" in rsrc and isrepository(rsrc["URL"]):
        gitdir = get_resource_location(rsrc,config)
        if args.dry:
            logger.info(f"git -C {gitdir} {' '.join(args.gitcommands)}")
        else:
            os.system(f"git -C {gitdir} {' '.join(args.gitcommands)}")
    
def copy_resource(rsrc,args,config, accum):
    source_dir = get_resource_location(rsrc,config)
    destination = os.path.join(args.DIRECTORY,rsrc['id']+'/')
    if args.clean and os.path.isdir(destination):
        logger.info(f"removing {destination}")
        shutil.rmtree(destination)
    
    rules = set()
    if config.copy.filters:
        logger.debug("config.copy.filters = {}".format(config.copy.filters))
        for filter in config.copy.filters:
            if (r:=_apply_filter(rsrc,filter)):
                rules = rules|r
            else:
                print(f"Excluding {rsrc['id']}.")
                return
    logger.debug("Copy: Rules={}".format(rules))
    
    logger.info(f"Copying {rsrc['id']} data from {source_dir} to {destination}")
    if not args.dry:
        copy_tree(source_dir, destination, destination, rules)

    if config.copy.destination_gitignore:
        _append_gitignore(rsrc['id']+'/', args.DIRECTORY)

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


     

def clone_resources(rsrc,args,config=None,accum=None)->None:
    if "URL" in rsrc:
        if isrepository(rsrc['URL']):
            destination = get_resource_location(rsrc,config)
            os.system(f"git clone {rsrc['URL']} {destination}")

def rename_resource(rsrc, args, accum):
    raise Exception("Unimplemented")


def show_resource(rsrc, args, config, accum):
    if _apply_filter(rsrc, {"match": {"id":args.REGEX}}):
        print(yaml.dump(rsrc))

def main()->int:
    parser = argparse.ArgumentParser(prog='aurore', description="Description text.")
    parser.add_argument("-C","--cache-file",  nargs="+", action="extend")
    parser.add_argument("-F","--field-filter",nargs="+", action="extend")
    parser.add_argument("-B","--base-uri", default="")
    parser.add_argument("-S","--setting-file",default="~/.local/share/aurore/aurore.yaml")
    parser.add_argument("-v","--verbose", action="count", default=0)
    parser.add_argument("-q","--quiet", action="store_true")
    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]

    subparsers = parser.add_subparsers(title='subcommands') #,description='list of subcommands',help='additional help')
    
    #-Clone-----------------------------------------------------------
    clone_parser = subparsers.add_parser('clone',help='clone repositories')
    clone_parser.add_argument('collection')
    clone_parser.set_defaults(func=clone_resources)
    
    #-Post-------------------------------------------------------------
    git_parser = subparsers.add_parser("post", help="create new entity")
    git_parser.add_argument("type")
    git_parser.add_argument("location", nargs="?", default="$$lid/metadata.xml")
    git_parser.set_defaults(initfunc=post_init)
    git_parser.set_defaults(func=None)
    git_parser.set_defaults(closefunc=post_close)

    #-Get-------------------------------------------------------------
    git_parser = subparsers.add_parser("get", help="retrieve an entity")
    git_parser.add_argument("-n","--name")
    git_parser.set_defaults(initfunc=get_init)
    git_parser.set_defaults(func=get_item)
    git_parser.set_defaults(closefunc=get_close)

    #-Update----------------------------------------------------------
    update_parser= subparsers.add_parser('update',
                        help='update resource metadata files.')
    update_parser.add_argument('metafile')
    update_parser.add_argument('-c','--commit',action='store_true')
    update_parser.set_defaults(func=update_src_metadata)
        
    #-Feed----------------------------------------------------------
    report_parser= subparsers.add_parser('feed',
                        help='report resource metadata files.')
    report_parser.add_argument("-t",'--template',default="tmpl-0004")
    report_parser.add_argument("-p","--print",nargs="+",action="extend",default=[])
    # report_parser.add_argument("-D","--collection", nargs="+", action="extend")
    report_parser.add_argument('--title')
    report_parser.add_argument('-d','--template_data')
    report_parser.set_defaults(init=init_report)
    # report_parser.set_defaults(initfunc=report_header_std)

    #-Copy------------------------------------------------------------
    copy_parser = subparsers.add_parser('copy',
                            help='copy resource files to DIRECTORY')
    # copy_parser.add_argument("collection")
    copy_parser.add_argument("DIRECTORY")
    copy_parser.add_argument("--clean",action="store_true")
    copy_parser.add_argument("--dry", action="store_true")
    # copy_parser.add_argument("-F","--filter")
    copy_parser.add_argument("-R","--rule")
    copy_parser.set_defaults(func=copy_resource)

    #-Show------------------------------------------------------------
    show_parser = subparsers.add_parser("show",help="show resources with id matching REGEX")
    show_parser.add_argument("collection")
    show_parser.add_argument("REGEX")
    show_parser.set_defaults(func=show_resource)

    # generate_git_API(subparsers)

    #-----------------------------------------------------------------
    # Main
    #-----------------------------------------------------------------
    args = parser.parse_args()
    logging.basicConfig(level=levels[args.verbose])
    if args.quiet: logger.setLevel(levels[0])

    #-Config----------------------------------------------------------
    config = Config(args.setting_file)

    config.environ = {
        "$FEDEASLAB_DEV": "/mnt/c/Users/claud/git/fcf"
    }
    # config.filters: list = []

    # config.copy = CopyConfig()
    # config.copy.destination_gitignore = True
    # config.copy.filters: list = []

    # import aurore
    # default_loc = os.path.join(os.path.dirname(os.path.abspath(aurore.__file__)),"defaults")
    # config.init_type = {
    #     "assm": os.path.join(default_loc,"init-assm.xml"),
    #     "assm/fcf": os.path.join(default_loc,"init-fcf.xml"),
    #     "qfem": os.path.join(default_loc,"qfem-init.xml"),
    #     "weuq": os.path.join(default_loc,"weuq-init.xml"),
    # }

    #-Main-----------------------------------------------------------

    accum = {}
    if args.base_uri:
        pass
    else:
        args.base_uri = config.base_uri
    
    namespace = config.namespace

    #-Filters-----------------------------------------------------------
    if config.field_filter:
        args.field_filter.extend(config.field_filter)
    
    FILTERS = {}
    if args.field_filter:
        for fltr in args.field_filter:
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
    if "init" in args:
        args.initfunc, args.func, args.closefunc = args.init(args,config)

    #-------------------------------------------------------------------
    if "initfunc" in args:
        accum = args.initfunc(args,config)
    else:
        accum = {}

    # print(f"namespace: {namespace}")
    if args.func:
        if isinstance(namespace,dict):
            for name, ref in namespace.items():
                resource: ElementTree = resolve_uri(os.path.join(args.base_uri , ref))
                if apply_field_filters(resource,FILTERS):
                # if True:
                    logger.info("Entering {}".format(name))
                    accum = args.func(resource, args, config, accum)
        if isinstance(namespace,ElementTree):
            for name, ref in namespace.iter():
                resource: ElementTree = resolve_uri(os.path.join(args.base_uri , ref))
                if apply_field_filters(resource,FILTERS):
                # if True:
                    logger.info("Entering {}".format(name))
                    accum = args.func(resource, args, config, accum)
        else:
            for ref in namespace:
                resource: ElementTree = resolve_uri(ref)
                logger.info("Entering {}".format(ref))
                accum = args.func(resource, args, config, accum)
    
    if "closefunc" in args:
        args.closefunc(args, config, accum)
    
    return 0

if __name__ == "__main__": main()
