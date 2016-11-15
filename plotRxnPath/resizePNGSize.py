"""
Resize the structure png file to make it visible in the reaction pathway diagram.
Please adjust the factor `f` accordingly.
Peng Zhang
Nov-14-2016
"""

import os
from PIL import Image

structureDir = 'structure'
for filename in os.listdir(structureDir):
    if filename.endswith(').png'):
        filename = os.path.join(structureDir, filename)
        im = Image.open(filename)
        # f = 200.0/max(im.width, im.height)
        f = 3
        im = im.resize((int(im.width*f), int(im.height*f)))
        im.save(filename)

