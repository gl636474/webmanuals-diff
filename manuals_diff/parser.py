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
    
    def _strip_whitespace(self, text: str):
        """Removes all whitespace from start and end of text and replaces all
        sequences of whitespace in the middle of the text with a single 'normal'
        space."""
        text = text.strip()
        text = re.sub('[\s+]', ' ', text)
        return text

    def revision(self):
        """Return the revision informaion from the page header (bottom row,
        right most cell)."""
        
        # The last cell of the last row in the first table
        # contains a string of the form "Issue 2 / Revision 10"
        text = self._d("table:first tbody tr:last td:last").text()

        return self._strip_whitespace(text)

    def title(self):
        """Return the title from the page header (top row, middle/second cell - 
        which has row span of 3)."""
        
        text = self._d("table:first tbody tr:first td:nth-child(2)").text()
        
        return self._strip_whitespace(text)
    
    def date(self):
        """Return the date from the page header (top or second row, last cell).
        May or may not be present. Searches for the cell containing 'Date' and
        returns the content of the next cell. Returns None if no such cell."""
        
        date_header_cell = self._d("table:first tbody tr td:contains('Date')")
        if date_header_cell:
            text = date_header_cell.next('td').text()
            return self._strip_whitespace(text)
        else:
            return None

    
    def page_number(self):
        """Return the page number from the page header (top or second row, last
        cell). May or may not be present. Searches for the cell containing
        'Page' and returns the content of the next cell. Returns None if no such
        cell exists."""
        
        date_header_cell = self._d("table:first tbody tr td:contains('Page')")
        if date_header_cell:
            text = date_header_cell.next('td').text()
            return self._strip_whitespace(text)
        else:
            return None