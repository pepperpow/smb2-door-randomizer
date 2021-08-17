import setuptools
import cx_Freeze, sys

with open("README.md", "r") as fh:
    long_description = fh.read()

# setup_desc = {
#     "name": "game_lib", # Replace with your own username
#     "version": "0.0.2",
#     "description": "A small example package",
#     "author": "Example Author",
#     "author_email": "author@example.com",
#     "long_description": long_description,
#     "long_description_content_type": "text/markdown",
#     "url": "N/A",
#     "packages": setuptools.find_packages(),
#     "classifiers": [
#         "Programming Language: : Python: : 3",
#         "License: : OSI Approved: : MIT License",
#         "Operating System: : OS Independent",
#     ],
#     "python_requires": '> 3.6',
# }

# setuptools.setup(**setup_desc)

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

freeze_desc = {
    "name": "pepperpow", # Replace with your own username
    "version": "0.49",
    "description": "A small example package",
    "options":{
        "build_exe": {'include_files': ['extras', 'icons', 'my_characters', 'my_levels', 'patch_data', 'README.md']}
    } ,
    "executables": [
    cx_Freeze.Executable(
        'smb2_door_randomizer.py', base=base, targetName="smb2_door_randomizer.exe", icon='icons/iconApp.ico'
    ),
    cx_Freeze.Executable(
        'raw_to_tiled.py', targetName="raw_to_tiled.exe", icon='icons/iconEx.ico',
    )
    ]
}

cx_Freeze.setup(**freeze_desc)

