#!python3

from pathlib import Path
from time import time
from manuals_diff import WebManualsServer
from manuals_diff import WebManualsPageParser

OMA_MANUAL_ID = 5563
FSI_MANUAL_ID = 12657

dest_dir = Path("/Users/gareth/Documents/Programming/eclipse-workspace-python/Webmanuals Diff")

#username = input("Username: ")
#password = input("Password: ")
server = WebManualsServer(cache_dir=dest_dir, offline=True)

start_time = time()

oma_downloader = server.get_manual(OMA_MANUAL_ID)
oma_dir = oma_downloader.download()

fsi_downloader = server.get_manual(FSI_MANUAL_ID)
fsi_dir = fsi_downloader.download()

end_time = time()
total_time = end_time - start_time
print("Took {} seconds to download/check docs".format(total_time))


# Now parse a page of a manual

manual_id = OMA_MANUAL_ID
downloader = oma_downloader
page_number = 9



file = downloader.get_page_file(page_number)
page_id = downloader.manual_metadata.get_page_id(page_number)

p = WebManualsPageParser(file, page_id, page_number, manual_id)
print(p.revision())
print(p.title())
print(p.date())
print(p.page_number())
#print(p.sanitised_content())
print(p.sanitised_wiki_markup())
