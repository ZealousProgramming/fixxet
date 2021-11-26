## fixxet
__fixxet__ is a simple command-line script that will display all TODOs and FIXMEs.

__*CURRENTLY ONLY TESTING ON WINDOWS*__


### Usage
```python
# This will run setting the root directory to the current working directory.
fixxet run

# For help:
fixxet -h
fixxet --help

# List builtin filters
fixxet filter

# Set the root to the currect directory, and use a whitelist of .py, and .json.
fixxet run -wle .py .json

# Use a whitelist for .py, .json extentions, and append cimport to the exclude filter.
fixxet run -wle .zig -ef cimport.zig

# Set the root to ./src
fixxet run ./src -wle .zig -ef cimport.zig
```

### Future Features
- [x] Append Directories to the Exclude filter with `-ed`
- [x] Append filename to the Exclude filter with `-ef`
- [x] Add commands to the cli syntax
- [x] Add `run` for running fixxet.
- [x] Get standard builtin exclude folders and file extensions command `filter`
- [ ] Add Option to print out filenames when searching `-p`
- [ ] Linux Build
- [ ] Determine the language for the file and look for the comment syntax of that language.
- [ ] Setup script
