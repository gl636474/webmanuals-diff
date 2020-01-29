'''
Created on 18 Dec 2019

@author: gareth
'''
import json
from pathlib import Path

class WebManualsManualMetadata:
    """Represents meta data about a particular Web Manuals manual. The following
    properties can will provide infrmation:
    
    revision_name - human readable version information as a string
    revision_id - a computer readable revision number as a number
    id - the ID number of the manual.
    """
    
    class WebManualsChapter:
        """Represents a chapter of teh manual - with a name and an ordered list
        of pages."""
        def __init__(self, name: str = ""):
            self.name = name
            self.pages = list()
    
    _save_file_encoding = "UTF-8"
    
    _metadata_filename = "metadata.json"
    
    def __init__(self, cache_dir: Path):
        """Creates a new metadata object which will parse Webmanuals JSON
        manual metadata. Parsed metadata will be cached in and read from the
        supplied directory.
        
        One (or both) of load_from_cache() and parse_json() should be called to
        instantiate the instance properties."""
        
        cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_filename = cache_dir / WebManualsManualMetadata._metadata_filename
        self.clean()
    
    def clean(self):
        """Sets all properties to None."""
        self.id = None
        self.name = None
        self.revision_id = None
        self.revision_name = None
        self.chapters = None
        
        self._pages = None
    
    def load_from_cache(self):
        """Attempts to load metadata from the saved metadata file in the
        cache_dir directory supplied in the constructor. Returns True if cached
        metadata was successfully loaded or False otherwise (if file was not
        present or was invalid)."""
    
        if self._cache_filename.is_file():
            try:
                # Read from file then parse
                with self._cache_filename.open(encoding=WebManualsManualMetadata._save_file_encoding) as stream:
                    file_contents = stream.read()
                    
                loaded_metadata = json.loads(file_contents)
                self.parse_json(loaded_metadata, cache_it=False)
                return True
            
            except:
                self.clean()
                return False
        else:
            return False

    def parse_json(self, json_dict: dict, cache_it: bool = True):
        """Parse the supplied JSON and sets up the instance properties.
        Optionally saves the parsed JSON in a file in the cache_dir supplied in
        the constructor to be read by load_from_cache()."""
        
        try:
            self.revision_name = json_dict["revisionName"]
            self.revision_id = json_dict["revisionId"]
            self.id = json_dict["manualId"]
        except KeyError as key_error:
            raise ValueError("Metadata does not contain required key: {}"
                             .format(str(key_error)))
            
        try:
            self.name = json_dict["chapters"][0]["pages"][0]["name"]
        except:
            self.name = "Unknown"

        # list of WebManualsChapter
        self.chapters = list()
        
        try:
            for chapter in json_dict["chapters"]:
                new_chapter = self.add_chapter(chapter["name"])
                for page in chapter["pages"]:
                    new_chapter.pages.append(page["id"])
        except KeyError as key_error:
            raise ValueError("Metadata does not contain required key: {}"
                             .format(str(key_error)))
        
        if cache_it:
            metadata_as_string = json.dumps(json_dict, indent=2)
            with self._cache_filename.open(mode='w', encoding=WebManualsManualMetadata._save_file_encoding) as stream:
                print(metadata_as_string, file=stream)

    def add_chapter(self, name: str = ""):
        """Adds another (optionally named) chapter to the end of the current
        list of chapters. Pages can then be added to the chapter via the
        add_page() method."""
        new_chapter = WebManualsManualMetadata.WebManualsChapter(name)
        self.chapters.append(new_chapter)
        
        # Discard old page cache 
        self._pages = None
            
        return new_chapter
    
    def get_last_chapter(self):
        """Returns the number of the last chapter in this manual. If no chapters
        exist, returns -1."""
        if isinstance(self.chapters, list):
            # Returns -1 for empty list
            return len(self.chapters) - 1
        else:
            # Unitinitalised!
            return -1
    
    def add_page(self, page_id: int, chapter: int = 0):
        """Adds another page to the end of the specified chapter (default
        chapter 0) which has the supplied page ID. Raises exception if the
        specified chapter does not exist."""
        
        # NB: chapter numbers are 0-based
        last_chapter = self.get_last_chapter()
        if last_chapter >= 0 and chapter <= last_chapter:
            self.chapters[chapter].pages.append(page_id)
            # Discard old page cache 
            self._pages = None
        else:
            raise ValueError("Manual '{}' has no chapter {} (last chapter: {})"
                             .format(self.name, chapter, last_chapter))
        
    def get_pages(self, chapter_number: int = -1):
        """Gets the list of page IDs for the specified chapter_number or for the
        entire manual if chapter_number is -1 or not supplied."""
        
        if chapter_number < 0:
            return self.get_all_pages()
        
        else:
            # NB: chapter numbers are 0-based
            last_chapter = self.get_last_chapter()
            if chapter_number <= last_chapter:
                return self.chapters[chapter_number].pages
            else:
                raise ValueError("Manual '{}' has no chapter {} (last chapter: {})"
                                 .format(self.name, chapter_number, last_chapter))
    def get_all_pages(self):
        """Gets the list of page IDs for the entire manual. This is cached on
        first access. The cache will be nulled if add_page() or add_chapter() is
        called."""
        
        if self._pages == None:
            self._pages = list()
            for chapter in self.chapters:
                self._pages.extend(chapter.pages)
        
        return self._pages
                        
    def get_page_id(self, page_number: int):
        """Returns the ID of the specified page number. Page numbers are
        zero-indexed."""
        return self.get_all_pages()[page_number]
    
    def get_number_pages(self):
        """Returns the number of pages in the manual."""
        return len(self.get_all_pages())

        