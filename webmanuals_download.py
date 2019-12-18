#!python3

from pathlib import Path
from manuals_diff import WebManualsDownloader

wmd = WebManualsDownloader()
wmd.download_manual(5563, 'gladd', 'gladd', Path("/Users/gareth/Documents/Programming/eclipse-workspace-python/Webmanuals Diff"))

