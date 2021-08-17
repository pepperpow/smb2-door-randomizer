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

freeze_desc = {
    "name": "pepperpow", # Replace with your own username
    "version": "0.5",
    "description": "A small example package",
    "executables": [cx_Freeze.Executable(
        'smb2_door_randomizer.py', base="Win32GUI", targetName="SMB2DR.exe"
    )]
}

cx_Freeze.setup(**freeze_desc)

