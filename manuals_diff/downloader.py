'''
Created on 18 Dec 2019

@author: gareth
'''
import requests
from pathlib import Path
from .metadata import WebManualsManualMetadata

class WebManualsManualDownloader:
    """Downloads a particular manual from a WebManuals site. Once an object has
    been instantited, the properties can be used to obtain data about the
    manual. Call download() to actually download the pages to a directory.
    """

    def __init__(self,
                 session: requests.Session,
                 manual_id: int,
                 metadata_url: str,
                 page_url: str,
                 destination: Path):
        """Creates a downloader to download the specified manual from
        WebManuals. The session must already be logged into the site. The
        given URLs will be used to fetch the metadata and the pages. These
        URLs should not include the query parameters - they will be added by
        methods in this class.
        
        Files will be written to disk as they are downloaded. Any previous
        download will be continued from the point it ended."""
    
        self.page_url = page_url
        self.session = session
        self.destination_dir = destination

        # Get MetaData for manual
        self.manual_metadata = WebManualsManualMetadata(self.destination_dir)
        if not self.manual_metadata.load_from_cache():
            # Not cached, must download it
            params={
                "manualId": str(manual_id),
                "revision": "undefined"
                }
            meadata_response = self.session.post(metadata_url, params=params)
            meadata_response.raise_for_status() # no-op if 2xx response code
        
            # Also caches the downloaded metadata 
            self.manual_metadata.parse_json(meadata_response.json())

    @property
    def revision(self):
        """The revision of this manual in English, e.g. 'Issue 6'"""
        return self.manual_metadata.revision_name
    
    @property
    def revision_id(self):
        """The revision of this manual as a computer-readable number/string."""
        return self.manual_metadata.revision_id
    
    @property
    def name(self):
        """The name of this manual, e.g. 'OMA'."""
        return self.manual_metadata.name
    
    @property
    def id(self):
        """The ID of this manual, e.g. 5536."""
        return self.manual_metadata.id
        
    def download(self):
        """Actually download the pages of this manual into the destination
        directory specified in the constructor. The directory will be created if
        it does not already exist. Pages will only be downloaded if there is not
        already a file for that page present in the destination directory 
        supplied in the constructor."""
        
        self.destination_dir.mkdir(parents=True, exist_ok=True)
        
        page_number = 0
        for chapter in self.manual_metadata.chapters:
            for page_id in chapter.pages:
                dest_file = self.destination_dir / "page{:08d}".format(page_number)
                
                if not dest_file.is_file():
                    text = self._get_page_snippet(page_id)
                    self._write_to_file(text, dest_file)
                
                page_number += 1

    def _write_to_file(self, text: str, file_path: Path):
        """Writes the specified text string to a file at the specified path. Any
        existing file will be truncated."""
        try:
            with file_path.open("w") as stream:
                print(text, file=stream)
        except:
            if file_path.exists():
                file_path.unlink()
            raise


    def _get_page_snippet(self, page_id: int):
        """Returns the specified page from WebManuals as a text string."""
        params ={
            "pageId": page_id,
            "layoutMode": "normal"
            }
        page_response = self.session.get(self.page_url, params=params)
        
        # This is a no-op if the HTTP response code was 2xx. If there was an
        # error, the exception error message will include the HTTP params
        # so the caller will know which page errored
        page_response.raise_for_status()

        return page_response.text

        




