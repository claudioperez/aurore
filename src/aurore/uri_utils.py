import os
import xml.etree.ElementTree as ElementTree
from urllib.parse import urlparse

def resolve_uri(ref:str)->ElementTree:
    ref = os.path.expandvars(ref)
    # print(ref)
    url = urlparse(ref)
    if os.path.isfile(url.path):
        _, ext = os.path.splitext(url.path)
        if ext in ["xml",".xml"]:
            item = ElementTree.parse(url.path)

    else:
        return
    if url.fragment:
        return item.find(f".//*[@id='{url.fragment}']")
            
