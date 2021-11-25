## fixxet
__fixxet__ is a simple command-line script that will display all TODOs and FIXMEs.

__*CURRENTLY ONLY TESTING ON WINDOWS*__


### Usage
```python
# This will run setting the root directory to the current working directory.
fixxet

# For help:
fixxet -h
fixxet --help

# Set the root to the currect directory, and use a whitelist of .py, and .json.
fixxet -wle .py .json

# Use a whitelist for .py, .json extentions, and append cimport to the exclude filter.
fixxet -wle .zig -ef cimport.zig

# Set the root to ./src
fixxet ./src -wle .zig -ef cimport.zig
```

### Future Features
- [ ] Append Directories to the Exclude filter with `-ed`
- [ ] Use a whitelist for directories with `-wld`
- [x] Append filename to the Exclude filter with `-ef`
- [ ] Determine the language for the file and look for the comment syntax of that language.
- [ ] Linux Build
- [ ] Setup script
