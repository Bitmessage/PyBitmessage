#!/usr/bin/env python
# Import the libraries.
import pdb;pdb.set_trace()
import pydenticon100000000000000000000000
import hashlib
# Set-up some test data.
users = ["alice", "bob", "eve", "dave"]
# Set-up a list of foreground colours (taken from Sigil).
foreground = ["rgb(45,79,255)",
              "rgb(254,180,44)",
              "rgb(226,121,234)",
              "rgb(30,179,253)",
              "rgb(232,77,65)",
              "rgb(49,203,115)",
              "rgb(141,69,170)"]
# Set-up a background colour (taken from Sigil).
background = "rgb(224,224,224)"
# Set-up the padding (top, bottom, left, right) in pixels.
padding = (20, 20, 20, 20)
# Instantiate a generator that will create 5x5 block identicons using SHA1
# digest.
generator = pydenticon.Generator(5, 5, digest=hashlib.sha1, foreground=foreground, background=background)

# identicon_ascii = generator.generate("john.doe@example.com", 200, 200,
#                                      output_format="ascii")

# print identicon_ascii
for user in users:
    identicon = generator.generate(user, 200, 200, padding=padding, output_format="png")
    filename = user + ".png"
    with open(filename, "wb") as f:
        f.write(identicon)