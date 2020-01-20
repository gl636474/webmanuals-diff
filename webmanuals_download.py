#!python3

from pathlib import Path
from manuals_diff import WebManualsServer
from manuals_diff import WebManualsPageParser

OMA_MANUAL_ID = 5563
FSI_MANUAL_ID = 12657

dest_dir = Path("/Users/gareth/Documents/Programming/eclipse-workspace-python/Webmanuals Diff")

username = input("Username: ")
password = input("Password: ")
server = WebManualsServer(username, password, cache_dir=dest_dir)

oma_downloader = server.get_manual(OMA_MANUAL_ID)
oma_dir = oma_downloader.download()

fsi_downloader = server.get_manual(FSI_MANUAL_ID)
fsi_dir = fsi_downloader.download()



file = oma_dir / "page00000015"

p = WebManualsPageParser(file)
print(p.revision())
print(p.title())
print(p.date())
print(p.page_number())
#print(p.sanitised_content())
print(p.wiki_markup())
