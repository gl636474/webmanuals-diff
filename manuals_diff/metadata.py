'''
Created on 18 Dec 2019

@author: gareth
'''

class WebManualsManualMetadata:
    
    class WebManualsChapter:
        def __init__(self, name: str = ""):
            self.name = name
            self.pages = list()
    
    def __init__(self, metadata):

        try:
            self.revision_name = metadata["revisionName"]
            self.revision_id = metadata["revisionId"]
            self.id = metadata["manualId"]
        except KeyError as key_error:
            raise ValueError("Metadata does not contain required key: {}"
                             .format(str(key_error)))
            
        try:
            self.name = metadata["chapters"][0]["pages"][0]["name"]
        except:
            self.name = "Unknown"

        # list of WebManualsChapter
        self.chapters = list()
        
        for chapter in metadata["chapters"]:
            new_chapter = self.add_chapter(chapter["name"])
            for page in chapter["pages"]:
                new_chapter.pages.append(page["id"])
    
    def add_chapter(self, name: str = ""):
        new_chapter = WebManualsManualMetadata.WebManualsChapter(name)
        self.chapters.append(new_chapter)
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
        else:
            raise ValueError("Manual '{}' has no chapter {} (last chapter: {})"
                             .format(self.name, chapter, last_chapter))
        
    def get_pages(self, chapter_number: int = -1):
        """Gets the list of page IDs for the specified chapter_number or for the
        entire manual if chapter_number is -1 or not supplied."""
        
        if chapter_number < 0:
            pages = list()
            for chapter in self.chapters:
                pages.extend(chapter.pages)
            return pages
        
        else:
            # NB: chapter numbers are 0-based
            last_chapter = self.get_last_chapter()
            if chapter <= last_chapter:
                return self.chapters[chapter].pages
            else:
                raise ValueError("Manual '{}' has no chapter {} (last chapter: {})"
                                 .format(self.name, chapter, last_chapter))
                    
            