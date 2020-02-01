#!python3

from pathlib import Path
from time import time
from manuals_diff import WebManualsServer
from manuals_diff import WebManualsPageParser
from manuals_diff.fsibuilder import FsiWebManualsManualBuilder

OMA_MANUAL_ID = 5563
FSI_MANUAL_ID = 12657

dest_dir = Path("/Users/gareth/Documents/Programming/eclipse-workspace-python/Webmanuals Diff")

#username = input("Username: ")
#password = input("Password: ")
server = WebManualsServer(cache_dir=dest_dir, offline=True)

start_time = time()

#oma_downloader = server.get_manual(OMA_MANUAL_ID)
#oma_dir = oma_downloader.download()

fsi_downloader = server.get_manual(FSI_MANUAL_ID)
fsi_dir = fsi_downloader.download()

end_time = time()
total_time = end_time - start_time
print("Took {} seconds to download/check docs".format(total_time))
print()
print()

# Now parse a manual
start_time = time()

# TODO: merge parser and builder. Traverse the pyquery tree directly to produce
# wiki - specific markup. E.g.:
#
# parser = TikiWikiFsiWebManualsParser(fsi_downloader)
# markup = parser.parse()
# with fsi_file.open("w") as stream:
#     print(markup, file=stream)

fsi_file = dest_dir / "fsi.txt"
fsi_manual_builder = FsiWebManualsManualBuilder(fsi_file, fsi_downloader)
fsi_manual_builder.build()
end_time = time()
total_time = end_time - start_time
print("Took {} seconds to parse/concat pages".format(total_time))
