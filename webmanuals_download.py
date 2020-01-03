#!python3

from pathlib import Path
from manuals_diff import WebManualsServer
from manuals_diff import WebManualsPageParser

OMA_MANUAL_ID = 5563
FSI_MANUAL_ID = 12657

manual_id = FSI_MANUAL_ID

dest_dir = Path("/Users/gareth/Documents/Programming/eclipse-workspace-python/Webmanuals Diff")

#server = WebManualsServer('gladd', 'gladd')
#downloader = server.get_manual(manual_id)
#downloader.download(dest_dir)

file = dest_dir / "pages" / "page00000006"

p = WebManualsPageParser(file)
print(p.revision())
print(p.title())
print(p.date())
print(p.page_number())
print(p.wiki_markup())
