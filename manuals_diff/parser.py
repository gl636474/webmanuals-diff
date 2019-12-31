'''
Created on 18 Dec 2019

@author: gareth
'''

import pyquery
import re
from pathlib import Path

class WebManualsPageParser:
    """Reads in a downloaded Web Manuals manual page and parses it for revision
    information and content. The content is converted from HTML snippets to
    Wiki Markdown format.
    """
    def __init__(self, filename: Path):
        """Reads in the specified file ready for information to be accessed via
        the other methods of this class."""
        self._d = pyquery.PyQuery(filename=filename)
    
    def revision(self):
        """Return the revision informaion from the page header."""
        
        # The last cell of the last row in the first table in the first DIV
        # contains a string of the form "Issue 2 / Revision 10"
        text = self._d("div:first tbody:first tr:last td:last").text()

        # text() will preserve whitespace - of which there can be loads in HTML 
        text = text.strip()
        
        # Replace any sequences of whitespace in the middle of the string with
        # just a single 'normal' space
        text = re.sub('[\s+]', ' ', text)
        return text