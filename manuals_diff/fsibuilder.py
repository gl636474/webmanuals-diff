'''
Created on 30 Jan 2020

@author: gareth
'''

from .downloader import WebManualsManualDownloader
from .parser import WebManualsPageParser
from pathlib import Path

class FsiWebManualsManualBuilder:
    """Builds a wiki markup version of the FSIs manual from the previously
    downloaded files."""
    
    def __init__(self, dest_file: Path, downloader: WebManualsManualDownloader):
        """Created a new FSI builder."""
        self._dest_file = dest_file
        self._downloader = downloader
        
    def _slugify(self, text: str):
        """Returns the text with all whitespace stripped and lowercased."""
        return ''.join(text.split()).lower()
    
    def build(self):
        """Parse the downloaded files supplied in the constructor and create the
        wiki markup file in the location supplied in the constructor."""
        
        content = "{{MARKDOWN}}\n\n"
        current_title_slug = ""
        for page_number in range(0, self._downloader.manual_metadata.get_number_pages()):
        
            file = self._downloader.get_page_file(page_number)
            page_id = self._downloader.manual_metadata.get_page_id(page_number)
            
            parser = WebManualsPageParser(file, page_id, page_number,
                                          self._downloader.id)
        
            # TODO: track max revision and most recent date
        
            new_title = parser.title()
            if new_title and not new_title.isspace():
                new_title_slug = self._slugify(new_title)
                if current_title_slug != new_title_slug:
                    # New FSI/section
                    content += "\n\n# {}\n\n".format(new_title)
                    current_title_slug = new_title_slug
        
            content += parser.sanitised_wiki_markup()
        

        with self._dest_file.open("w") as stream:
            print(content, file=stream)
