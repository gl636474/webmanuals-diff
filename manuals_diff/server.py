'''
Created on 18 Dec 2019

@author: gareth
'''
from .downloader import WebManualsManualDownloader

import requests

class WebManualsServer:
    """Represents a WebManuals site from which manuals can be downloaded. Call
    get_manual() to obtain an object which can be used to download the manual.
    This object is reusable (can be usd to download many manuals) and is
    threadsafe."""

    def __init__(self,
                username: str,
                password: str,
                protocol: str = 'https',
                domain: str = 'babcock.webmanuals.aero',
                login_url_path: str = '/tibet/template/json%2CLoginUser.json',
                metadata_url_path: str =  '/tibet/template/json%2Creader%2CPages.json',
                page_url_path: str = '/tibet/template/Index.vm',
                site_id: int = 1140,
                thread_safe: bool = False):
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
        
        if self._session:
            # Doing things single-threaded
            return WebManualsManualDownloader(self._session, 
                                              manual_id, 
                                              self.metadata_url,
                                              self.page_url)
        else:
            # Doing things asynchronously - create session per downloader/thread
            session = self._create_session()
            return WebManualsManualDownloader(session, 
                                              manual_id, 
                                              self.metadata_url,
                                              self.page_url)



