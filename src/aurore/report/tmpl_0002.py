from ..utils import get_resource_location


def init(args,config):
    if "title" in args:
        print(f"""# {args.title}
## Build: `win-2020-10-31`

| ID  | Pass  | Notes  |   |
|---|---|---|---|""")
    return {}

def close(args,config,accum):
    print("## Data sources\n")
    if isinstance(args.datafile,list):
        for file in args.datafile:
            pass




def item(rsrc,args,config,accum={}):
    try:
        notes = rsrc['status'][0]['notes'].split('\n')
    except: notes = "~"

    print(f"""| `{rsrc['id']}`  | {rsrc['status'][0]['passing']} |  {notes[0]} |""")
    for note in notes[1:]:
        print(f"""|        |   |  {note} |""")

    return accum




