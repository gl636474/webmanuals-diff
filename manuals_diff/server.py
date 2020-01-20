'''
Created on 18 Dec 2019

@author: gareth
'''
from .downloader import WebManualsManualDownloader

import json
import requests
from pathlib import Path

class WebManualsServer:
    """Represents a WebManuals site from which manuals can be downloaded. Call
    get_manual() to obtain an object which can be used to download the manual.
    This object is reusable (can be usd to download many manuals) and is
    threadsafe."""

    _credentials_filename = "credentials.json"
    _credentials_file_encoding = "UTF-8"

    def __init__(self,
                username: str,
                password: str,
                protocol: str = 'https',
                domain: str = 'babcock.webmanuals.aero',
                login_url_path: str = '/tibet/template/json%2CLoginUser.json',
                metadata_url_path: str =  '/tibet/template/json%2Creader%2CPages.json',
                page_url_path: str = '/tibet/template/Index.vm',
                site_id: int = 1140,
                thread_safe: bool = False,
                cache_dir: Path = Path("~/.manuals_diff")):
        """Logs into a WebManuals server ready to download manuals via the
        get_manual() method. The protocol ('http' or 'https'), domain, URLs and
        site ID all default to the Babcock Web Manuals site and can be omitted.
        
        Only the log in username and password must be provided.
        
        If thread_safe is False (the default) then each manual downloader (as
        returned by get_manual()) will share the same requests (HTTP) session -
        so only one login will be performed. If thread_safe is True then each
        downloader will have their own session. This is provided because there
        is some discrepency in the documentation as to whether requests.Session
        is thread safe."""
    
        self.base_url = protocol + '://' + domain
        self.login_url = self.base_url + login_url_path
        self.metadata_url = self.base_url + metadata_url_path
        self.page_url = self.base_url + page_url_path

        self.username = username
        self.password = password
        self.site_id = site_id
        self._chache_dir = cache_dir
        
        self._set_up_username_password()
        
        if thread_safe:
            # Just check we can log in. Sesions will be created one for each
            # downloader
            session = self._create_session()
            session.close()
            self._session = None
        else:
            # Create and save the session which will be shared by every
            # downloader. This way we only log in once.
            self._session = self._create_session()

    def _set_up_username_password(self):
        """If username and/or password are None, attempts to read the missing
        one(s) from file. If username and/or password are set and different from
        those cached then writes them to file. The cached credentials are then
        used in subsequent batch mode operations."""
        
        credentials_file = self._chache_dir / self._credentials_filename
        if credentials_file.is_file():
            with credentials_file.open("r", encoding=self._credentials_file_encoding) as stream:
                file_contents = stream.read()
            # Get user/pass from file with default
            loaded_metadata = json.loads(file_contents)
            cached_username = loaded_metadata.get("username", None)
            cached_password = loaded_metadata.get("password", None)
        else:
            cached_username = None
            cached_password = None
           
        supplied_username = self.username
        supplied_password = self.password
        
        self.username = supplied_username or cached_username
        self.password = supplied_password or cached_password
        
        if self.username == None or self.password == None:
            raise ValueError("username and/or password not supplied and no values cached")
        
        # Write file if user or pass has changed
        if (cached_username == None or cached_username != supplied_username or
            cached_password == None or cached_password != supplied_password):
            
            json_credentials = {"username": self.username, "password": self.password}
            string_credentials = json.dumps(json_credentials, indent=2)
            with credentials_file.open("w", encoding=self._credentials_file_encoding) as stream:
                print(string_credentials, file=stream)
            
         
    def _create_session(self):
        """Creates a requests module Session object which has already logged
        into WebManuals site."""

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
            "password": self.password,
            "siteId": str(self.site_id),
            "username": self.username}
        login_response = session.post(self.login_url, data=login_payload)
        login_response.raise_for_status() # no-op if 2xx response code

        return session

    def close(self):
        """Closes any open session. Further calls to get_manual() will result in
        asynchronous/thread safe calls."""
        if self._session:
            self._session.close()
            self._session = None

    def get_manual(self, manual_id: int):
        """Returns a WebManualsManualDownloader object which will download the
        specified manual."""
        
        destination_dir = self._chache_dir / str(manual_id)
        
        if self._session:
            # Doing things single-threaded - reuse existing session
            session = self._session
        else:
            # Doing things asynchronously - create session per downloader/thread
            session = self._create_session()
            
        return WebManualsManualDownloader(session, 
                                          manual_id, 
                                          self.metadata_url,
                                          self.page_url,
                                          destination_dir)



