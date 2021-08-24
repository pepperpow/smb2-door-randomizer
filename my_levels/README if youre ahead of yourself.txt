README

Making a level pack requires a few things

1. Tiled Editor.  It's free to download but feel free to pay!!

2. A folder name for your level set

3. 10 json files per level, 30 per world and maximum 210 levels

Start by copying the openworld set, and take a look at the format in Tiled.

<documentation is in progress...>

ROOM = #.json

LEVEL = 0.json, 1.json... 9.json

When developing a level, make sure they're properly connected.  A door pointer "doorptr" must connect to the next room in each level.

(difference between Generic Jar and PTR Jars are the former always connects to room 4 (4.json), the latter requires a doorptr)

If a room is not connected, then the room is NOT used by the randomizer.

<...>