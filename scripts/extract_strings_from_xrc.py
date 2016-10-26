import os
import sys
from xml.etree import ElementTree as et

if len(sys.argv) != 2:
    print("Usage %s xrc_file"%sys.argv[0])
input_file = sys.argv[1]
fname, ext = os.path.splitext(input_file)
dest_fname = "%s_strings.py"%fname
tree = et.parse(input_file)
translatable_tags = ["label", "title"]
outf = open(dest_fname, "w")
for tag in translatable_tags:
    for elem in tree.getroot().findall(".//%s"%tag):
        outf.write("_('%s')\n"%elem.text)
print("Done.")
outf.close()