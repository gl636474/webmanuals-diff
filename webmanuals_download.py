#!python3

from pathlib import Path
from manuals_diff import WebManualsServer
from manuals_diff import WebManualsPageParser

dest_dir = Path("/Users/gareth/Documents/Programming/eclipse-workspace-python/Webmanuals Diff")

server = WebManualsServer('gladd', 'gladd')
downloader = server.get_manual(5563)
downloader.download(dest_dir)

file = dest_dir / "pages" / "page00000006"

p = WebManualsPageParser(file)
print(p.revision())
