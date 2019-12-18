'''
Created on 18 Dec 2019

@author: gareth
'''
import requests
from pathlib import Path
from .metadata import WebManualsManualMetadata
import shutil

class WebManualsDownloader:
    
    
    def __init__(self, 
                protocol: str = 'https',
                domain: str = 'babcock.webmanuals.aero',
                login_url_path: str = '/tibet/template/json%2CLoginUser.json',
                metadata_url_path: str =  '/tibet/template/json%2Creader%2CPages.json',
                page_url_path: str = '/tibet/template/Index.vm',
                site_id: int = 1140):
    
        self.base_url = protocol + '://' + domain
        self.login_url = self.base_url + login_url_path
        self.metadata_url = self.base_url + metadata_url_path
        self.page_url = self.base_url + page_url_path
        self.site_id = str(site_id)
        
    def download_manual(self, manual_id: int, username: str, password: str, destination: Path):
        
        pages_dir = destination / "pages"
        shutil.rmtree(pages_dir, ignore_errors=True)
        pages_dir.mkdir()
        
        # Create a session
        session = requests.Session()
        session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en;q=0.5"
            })
        homepage_response = session.get(self.base_url)
        homepage_response.raise_for_status() # no-op if 2xx response code
        
        # Log in
        login_payload = {
            "acceptedTou": "true",
            "action": "LoginUser",
            "password": password,
            "siteId": self.site_id,
            "username": username}
        login_response = session.post(self.login_url, data=login_payload)
        login_response.raise_for_status() # no-op if 2xx response code
        
        # Get MetaData for manual
        params={
            "manualId": str(manual_id),
            "revision": "undefined"
            }
        meadata_response = session.post(self.metadata_url, params=params)
        meadata_response.raise_for_status() # no-op if 2xx response code
        
        manual_metadata = WebManualsManualMetadata(meadata_response.json())
        
        page_number = 0
        for chapter in manual_metadata.chapters:
            for page_id in chapter.pages:
                text = self._get_page_snippet(session, page_id)
                dest_file = pages_dir / "page{:08d}".format(page_number)
                self._write_to_file(text, dest_file)
                page_number += 1
                
        return manual_metadata

    def _write_to_file(self, text: str, file_path: Path):

        try:
            with file_path.open("w") as stream:
                print(text, file=stream)
        except:
            if file_path.exists():
                file_path.unlink()
            raise


    def _get_page_snippet(self, session: requests.Session, page_id: int):
        
        params ={
            "pageId": page_id,
            "layoutMode": "normal"
            }
        page_response = session.get(self.page_url, params=params)
        
        # This is a no-op if the HTTP response code was 2xx. If there was an
        # error, the exception error message will include the HTTP params
        # so the caller will know which page errored
        page_response.raise_for_status()

        return page_response.text

        




