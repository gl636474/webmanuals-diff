'''
Created on 18 Dec 2019

@author: gareth
'''
import requests
from pathlib import Path
from .metadata import WebManualsManualMetadata
import shutil

class WebManualsManualDownloader:
    """Downloads a particular manual from a WebManuals site. Once an object has
    been instantited, the properties can be used to obtain data about the
    manual. Call download() to actually download the pages to a directory.
    """

    def __init__(self,
                 session: requests.Session,
                 manual_id: int,
                 metadata_url: str,
                 page_url: str):
        """Creates a downloader to download the specified manual from
        WebManuals. The session must already be logged into the site. The
        given URLs will be used to fetch the metadata and the pages. These
        URLs qhould not include the query parameters - they will be added by
        methods in this class."""
    
        self.page_url = page_url
        self.session = session

        # Get MetaData for manual
        params={
            "manualId": str(manual_id),
            "revision": "undefined"
            }
        meadata_response = self.session.post(metadata_url, params=params)
        meadata_response.raise_for_status() # no-op if 2xx response code
        
        self.manual_metadata = WebManualsManualMetadata(meadata_response.json())

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
        
    def download(self, destination: Path):
        """Actually download the pages of this manual into the specified
        destination directory. The directory wil be emptied if it exists or
        will be created if it does not exist."""
        
        pages_dir = destination / "pages"
        shutil.rmtree(pages_dir, ignore_errors=True)
        pages_dir.mkdir()
        
        page_number = 0
        for chapter in self.manual_metadata.chapters:
            for page_id in chapter.pages:
                text = self._get_page_snippet(page_id)
                
                dest_file = pages_dir / "page{:08d}".format(page_number)
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

        




