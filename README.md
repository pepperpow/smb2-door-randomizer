# Super Mario Bros 2 Door Randomizer 0.49

## About

The Super Mario Bros 2 Door Randomizer (SMB2DR for short) is a randomizer for Super Mario Bros 2/USA written in python3.

### Releases

While currently under development, releases will be placed at https://github.com/pepperpow/smb2-door-randomizer/tags

### Thanks to

KMCK/Xkeeper - assembly/prog help

pako - graphics help

tetraly - discord support

loginsinex - initial understanding of levels thru editor

### Gameplay

On top of randomization, there are small gameplay changes on top of several features

As for features:

- Specify the length of the game in levels
- Add Lives, Health
- Detect secrets automatically
- Randomize palettes of the Sky and change world enemies and tiles
- Replace characters with random new ones, with their palettes, names, and stats rearranged
- New character sprites by Pako and Pepper
- Randomly invert a level into a mirror opposite of itself.
- Change Boss Health randomly
- New Character Select options
- Character Select via Select+LR
- Survival, which eliminates a character after all lives are lost
- Force Characters per room

Changes to gameplay:

- POW Blocks can be hit from beneath
- Mushroom Blocks lifted from below while as a tile
- Continue from last door on lives lost
- Character select on death
- Shell bounces on toss, hits player
- Player is now shorter when shrunk down
- Invulnerabilty when exiting a door/vine
- Carry potions and keys on vines
- Squat Jump while holding items (thanks spiderdave)
- Bugfixes built into smb2 asm by xkeeper
- and more...?

### TODO

This current version is a pared down completion of an original Door Randomizer.  New features will be added over the coming time...

Level Stringer:

- Does not patch levels completely so that they're all playable, and the method is rather simple
- World 7 Level 2 will softlock, as it hasn't been patched for it!!!  Deselect it in the Level Select menu

Boss Hunter

- Must select levels labeled with 'openworld'
- Not fully tested, but should be stable enough to complete at boss numbers up to 5

Known things to fix:

- Character sheets are not complete, missing some sprite replacements
- Some character sheets are also not aligned
- Jars are finnicky, no warps in game
- Picking up blocks from below can phase you down
- Inverted Levels/Hawkmouths can carry you into the wrong area (page offset)
- Some sprites/tiles not removed/remedied when converting worlds to others
- Level compressor is pretty bad/inaccurate...
- and more..........................

## Usage

In order to run the program, execute `smb2_door_randomizer.exe` or run `smb2_door_randomizer.py` from source.

A `Super Mario Bros 2 (U).nes` rom is required with the following PRGs or CRCs:


PRG0/REV0
- 47ba60fad332fdea5ae44b7979fe1ee78de1d316ee027fea2ad5fe3c0d86f25a
- 0x7D3F6F3D
- 0xE0CA425C


PRG1/REVA
- 6ca47e9da206914730895e45fef4f7393e59772c1c80e9b9befc1a01d7ecf724
- 0x8AA4ACE0
- 0x17518181

It may be placed in the root directory as `smb2.nes` to autoload, or loaded from in the window.

From This point forward, the options in the user interface as available to use.

TODO: More features will be implement and discussed here.

### Compile

To run from source, the following libraries are required

- `pillow`
- `pySimpleGui`

Compile the EXE with the following command and library:

 `python3 -m pip install cx_Freeze`

`python3 ./setup.py build`
