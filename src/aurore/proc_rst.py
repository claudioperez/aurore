import os
import re
from docutils.core import publish_doctree
import xml.etree.ElementTree as ElementTree


def rst_to_xml(filename):
    with open(filename,"r") as f:
        doctree = publish_doctree(f.read())
    return ElementTree.fromstring(doctree.asdom().toxml())

def find_dependencies(src: str, base:str)->list:
    rst_tree = rst_to_xml(
        os.path.expandvars(
            os.path.join(base,src)
        )
    )
    dependencies = []
    literal_includes = [
        i.text for i in rst_tree.findall(".//literal_block")
            if i.text and "literalinclude" in i.text
    ]
    paths = [
        i.split("\n")[0].split("literalinclude:: ")[1] for i in literal_includes
    ]
    dependencies.extend(paths)

    return dependencies, None


def parse_rst(text:str):
    doctree = publish_doctree(text).asdom()

    # Convert to etree.ElementTree since this is easier to work with than
    # xml.minidom
    doctree = ElementTree.fromstring(doctree.toxml())

    # Get all field lists in the document.
    field_lists = doctree.findall('field_list')

    fields = [f for field_list in field_lists \
        for f in field_list.findall('field')]

    field_names = [name.text for field in fields \
        for name in field.findall('field_name')]

    field_text = [ElementTree.tostring(element) for field in fields \
        for element in field.findall('field_body')]

    return dict(zip(field_names, field_text))
