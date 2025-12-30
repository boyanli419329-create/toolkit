"""
Defines paths to important files and folders inside the `toolkit` project.

Project structure
-----------------
toolkit/                <- TOOLKIT_DIR
|__ data/               <- DATA_DIR
|   |__ ...
|__ exercises/          <- EXERCISES_DIR
|   |__ ...
|__ projects/           <- PROJECTS_DIR
|   |__ ...
|__ lectures/           <- LECTURES_DIR
|   |__ ...
|__ toolkit_paths.py    <- This file

Usage
-----
This module provides variables that point to the main directories in the
project. You can use these variables in your code instead of hard-coding
file paths.

Example:
    from toolkit_paths import DATA_DIR
    prices_file = DATA_DIR / "prices.csv"

    In this case, the variable prices_file will point to:

    toolkit/
    |__ data/
    |   |__ prices.csv      <- prices_file

Implementation details
----------------------
1. We import the `pathlib` library, which provides tools for working with
   file system paths.
2. `__file__` is a special variable that stores the location of this file.
3. `TOOLKIT_DIR` is set to the parent folder of this file (the `toolkit`
   project folder).
4. Other directory variables (`DATA_DIR`, `EXERCISES_DIR`, `PROJECTS_DIR`,
   `LECTURES_DIR`) are created by joining `TOOLKIT_DIR` with the
   corresponding sub-folder names.

Notes
-----
- Please do not modify this file.
- All paths are represented as `pathlib.Path` objects.
"""

import pathlib

TOOLKIT_DIR = pathlib.Path(__file__).parent
DATA_DIR = TOOLKIT_DIR / 'data'
PROJECTS_DIR = TOOLKIT_DIR / 'projects'
LECTURES_DIR = TOOLKIT_DIR / 'lectures'
EXERCISES_DIR = TOOLKIT_DIR / 'exercises'


