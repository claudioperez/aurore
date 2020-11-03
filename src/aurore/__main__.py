#!/usr/bin/env python


import os, re, argparse, distutils, shutil, logging
from distutils import dir_util
import urllib.parse
from pathlib import Path

import yaml, coloredlogs
from oaks.lists import list_merge, test_item_by_key

from .core import Config, InitOperation, ItemOperation
from .report import item_test_report, report_header_std, report_footer_std
from .utils import copy_tree, get_resource_location

logger = logging.getLogger(__name__)
coloredlogs.install()
# coloredlogs.install(level="DEBUG",logger=logger)


class CopyConfig(Config): pass

config = Config()
config.environ = {
    "$FEDEASLAB_DEV": "/mnt/c/Users/claud/git/fcf"
}
config.copy = CopyConfig()
config.copy.destination_gitignore = True
config.copy.filters: list = []


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

def update_src_metadata(rsrc,args,config):
    destination_dir = get_resource_location(rsrc,config)
    try:
        destination = os.path.join(destination_dir,args.metafile)
        with open(destination,'w+') as mf:
            logger.info(f"Copying {rsrc['id']} data to {destination}")
            mf.write(yaml.dump(rsrc))
    except Exception as e:
        print(rsrc)
        print(e)
        return

    if args.commit and "URL" in rsrc:
        if isrepository(rsrc["URL"]):
            gitdir = get_resource_location(rsrc,config)
            os.system(f"git -C {gitdir} pull")
            os.system(f"git -C {gitdir} add {args.metafile}")
            os.system(f"git -C {gitdir} commit -am 'Auto-update {args.metafile}'")
            os.system(f"git -C {gitdir} push")

def copy_resource(rsrc,args,config):
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
    return set(filter["rules"])
        

def isrepository(url_string):
    url_object = urllib.parse.urlparse(url_string)
    url_path = Path(url_object.path)
    if len(url_path.parts)==3:
        return True
    else:
        return False

def clone_resources(rsrc,args,config=None):
    if "URL" in rsrc:
        if isrepository(rsrc['URL']):
            destination = get_resource_location(rsrc,config)
            os.system(f"git clone {rsrc['URL']} {destination}")

def generate_git_API(subparser):
    commands = {
        "clone": "",
        "fetch": {}
    }
    for command in commands:
        command_parser = subparser.add_parser(command,help=f"Interface to git {command}")
        command_parser.add_argument("datafile")
        def exec_command(rsrc,args):
            if "URL" in rsrc:
                if isrepository(rsrc):
                    destination = get_resource_location(rsrc,config)
                    os.system(f"git {command} ")

def rename_resource(rsrc,args):
    raise Exception("Unimplemented")

def main():
    parser = argparse.ArgumentParser(prog='aurore')
    parser.add_argument("-v","--verbose", action="count", default=0)
    parser.add_argument("-q","--quiet", action="store_true")
    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]

    subparsers = parser.add_subparsers(title='subcommands',description='list of subcommands',help='additional help')
    
    #-Clone-----------------------------------------------------------
    clone_parser = subparsers.add_parser('clone',help='clone repositories')
    clone_parser.add_argument('datafile')
    clone_parser.set_defaults(func=clone_resources)
    
    
    #-Update----------------------------------------------------------
    update_parser= subparsers.add_parser('update',
                        help='update resource metadata files.')
    update_parser.add_argument('datafile')
    update_parser.add_argument('metafile')
    update_parser.add_argument('-c','--commit',action='store_true')
    update_parser.set_defaults(func=update_src_metadata)
        
    #-Report----------------------------------------------------------
    report_parser= subparsers.add_parser('report',
                        help='report resource metadata files.')
    report_parser.add_argument('datafile',nargs="*")
    report_parser.add_argument('--title')
    report_parser.add_argument('-T','--template',action='store_true')
    report_parser.set_defaults(func=item_test_report)
    report_parser.set_defaults(initfunc=report_header_std)

    #-Copy------------------------------------------------------------
    copy_parser = subparsers.add_parser('copy',
                            help='copy resource files to DIRECTORY')
    copy_parser.add_argument("datafile")
    copy_parser.add_argument("DIRECTORY")
    copy_parser.add_argument("--clean",action="store_true")
    copy_parser.add_argument("--dry", action="store_true")
    copy_parser.add_argument("-F","--filter")
    copy_parser.set_defaults(func=copy_resource)

    #-Rename----------------------------------------------------------
    rename_parser = subparsers.add_parser('rename',
                            help='rename resource files to directory [destination_dir]')
    rename_parser.add_argument("datafile")
    rename_parser.add_argument("destination_dir")
    rename_parser.add_argument("--clean",action="store_true")
    rename_parser.set_defaults(func=rename_resource)

    # generate_git_API(subparsers)

    #-----------------------------------------------------------------
    # Main
    #-----------------------------------------------------------------
    args = parser.parse_args()
    logging.basicConfig(level=levels[args.verbose])
    if args.quiet: logger.setLevel(levels[0])

    if isinstance(args.datafile,list):
        db = {"references": []}
        for file in args.datafile:
            with open(file,"r") as f:
                newdata = yaml.load(f,Loader=yaml.Loader)
            db["references"] = list_merge(newdata["references"], db["references"], test_item_by_key("id"))
        # print("data: {}".format(db["references"]))
    else:
        with open(args.datafile,"r") as f:
            db = yaml.load(f,Loader=yaml.Loader)

    if "filter" in args:
        with open(args.filter,"r") as f:
            config.copy.filters.extend(yaml.load(f,Loader=yaml.Loader)["filters"])
    
    #-------------------------------------------------------------------
    if "initfunc" in args:
        args.initfunc(args,config)
    
    accum = []
    for resource in db['references']:
        logger.info("Entering {}".format(resource["id"]))
        accum.append(args.func(resource,args,config))
    
    if "closefunc" in args:
        args.closefunc(accum,args,config)

if __name__ == "__main__":
    main()
