'''
Created on 18 Dec 2019

@author: gareth
'''

import html2text
import pyquery
import re
from pathlib import Path

class WebManualsPageParser:
    """Reads in a downloaded Web Manuals manual page and parses it for revision
    information and content. The content is converted from HTML snippet to
    Wiki Markdown format.Note that none of these methods cache their return
    values so repeated calls will cause repeated processing.
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
        
    def raw_content(self):
        """Returns a string containing an HTML snippet - the part we are
        actually interested in - the bit that contains the manual content."""
        
        return self._d("div.compare-result-container").html()
    
    def sanitised_content(self, strip_non_ascii: bool = True):
        """Returns the raw content with the <span>s removed which gave hints to
        the previous content."""
        
        # content = self._d("div.controlledSectionView")
        content = self._d("div.compare-result-container")
        
        previous_value_spans = content("span.diff-html-removed")
        previous_value_spans.remove()
        
        previous_value_spans = content("span.wm-diff-delete-marker")
        previous_value_spans.remove()
        
        # Find empty links - Webmanuals deletes the text content but leaves the
        # outer <a href>!
        def is_empty(_, this):
            """Returns True if the given PyQuery element has no text inside it,
            i.e. is nothing or is just whitespace."""
            content = pyquery.PyQuery(this).text()
            return content == None or content.strip() == ''
        
        empty_a_elements = content("a").filter(is_empty)
        empty_a_elements.remove()
        
        # Wrap tables in a <p> so when converted to Markdown consecutive tables
        # aren't concatonated
        tables = content("table")
        tables.wrap("<p></p>")
        
        # Remove CSS float-clearing DIVs
        style_divs = content("div[style='clear: both; line-height: 1px;']")
        style_divs.remove()
        
        html_snippet = content.html()
        
        if strip_non_ascii:
            ascii_bytes = html_snippet.encode('ascii', errors='ignore')
            html_snippet = ascii_bytes.decode()
            
        return html_snippet
    
    def wiki_markup(self):
        """Returns a string containing wiki markup (in markdown format) of the
        manual content"""
        parser = html2text.HTML2Text()
        parser.ignore_links = False
        parser.body_width = 2000
        parser.wrap_links = False
        parser.protect_links = True
        parser.wrap_list_items = False
        parser.unicode_snob = True
        parser.pad_tables = False
        wiki_text = parser.handle(self.sanitised_content())
        return wiki_text
        