import re
from typing import List
import lxml


class PassthroughDict:
    """
    Like a Dict, but if the key is not in the dict, it returns the key instead.
    """

    def __init__(self, the_dict: dict): 
        self.the_dict = the_dict

    def __call__(self, key):
        """
        Get the value stored in the dict at `key`, or return the key.
        """
        return self.the_dict.get(key) or key


name_adjuster = PassthroughDict({
        "Quetcy Lozada": "Quetcy M. Lozada",
        "Kathrine Gilmore Richardson": "Katherine Gilmore Richardson",
        # Map Richardson to her whole last name, Gilmore Richardson.
        "Richardson": "Gilmore Richardson",
        # Legistar reports this last name with a ', but the city's site uses
        "O'Neill":"O’Neill",
    })

def from_x(els: List["lxml.etree._Element"]) -> str:
    """
    Given a list of xml elements, like from an xpath query, check its a singleton, and return its text, or ""
    """
    if len(els) != 1:
        return ""
    if isinstance(els[0], str): return els[0]
    return els[0].text

def content_from_x(els: List["lxml.etree.Element"]) -> str:
    if len(els) != 1:
        return ""
    if isinstance(els[0], str): 
        return els[0]
    return els[0].text_content().strip()

def get_last_name(full_name: str) -> str:
    name_parts = strip_name_end(full_name).split(" ")
    last_name = name_parts[-1]
    return name_adjuster(name_parts[-1])

def strip_name_end(full_name):
    """
    Remove Jr, III, etc. from names, if present.
    """
    return re.sub(r"(,? jr\.)|( i+ )", "", full_name, flags=re.I)

def pad_list(short, long, pad_with):
    """
    pad the short list with the pad_with until its as long as the long list
    """
    pad = [pad_with for _ in range(0, len(long)-len(short))]
    return short.extend(pad)


