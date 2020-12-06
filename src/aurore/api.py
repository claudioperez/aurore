import os
import subprocess
import xml.etree.ElementTree as ElementTree
import xml.dom.minidom as minidom

from datetime import datetime, timezone

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
    return {"items": []}

def get_item(rsrc, args:object, config:object, accum:dict)->dict:
    # print(rsrc)
    for el in rsrc.iter():
        if el.tag=="exe":
            proc_exe(el,args)
            # print(el.find("cli").text)
        elif el.tag=="":
            pass
    accum['items'].append(rsrc)
    return accum

def get_close(args, config, accum):
    for item in accum["items"]:
        # pass
        print(
            minidom.parseString(ElementTree.tostring(item)).toprettyxml(indent="  ")
            )

def proc_exe(rsrc,args):
    cli = rsrc.find("cli")
    build_loc = os.path.join(args.base_uri,rsrc.attrib["build-loc"])
    if "src" in cli.keys():
        if build_loc[-3:] == ".py":
            try:
                cli.text = subprocess.check_output([
                    "python", os.path.expandvars(build_loc), "--help"
                ]).decode().replace("<","&lt")
            except:
                pass
        else:
            try:
                cli.text = subprocess.check_output([
                    os.path.expandvars(build_loc)
                ]).decode().replace("<","&lt")
            except:
                try:
                    cli.text = subprocess.check_output([
                        os.path.expandvars(build_loc), "--help"
                    ]).decode().replace("<","&lt")
                except: 
                    pass
