What's this?
============

SkyBlock Challenge Manager is a small webservice built around
[Flask](http://flask.pocoo.org/) that tracks which challenges on the
[Skyblock](http://www.minecraftforum.net/topic/600254-surv-skyblock/) Minecraft
map you've completed.

Currently, the file `challenges.txt` represents the challenges of SkyBlock v2.1.
You can easily update the challenge set by updating the file `challenges.txt`
with the new set of challenges (one challenge text per line, concatenated with
the amount for challenges in the form do `amount` of X. See `challenges.txt`
for the exact format).

How to use
==========

You can either run SkyBlock Challenge Manager locally (assuming you've got
Linux) by running skyblock.py in a terminal. Or you can run SkyBlock Challenge
Manager as a WSGI script (you can use the provided skyblock.wsgi if you want).

License
=======

MIT, see COPYING for the full text.
