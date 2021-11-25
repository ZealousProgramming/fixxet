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
fixxet . -wl .py .json
```

### Future Features
- [ ] Append Directories to the Exclude filter with `-ed`
- [ ] Use a whitelist for directories with `-wld`
- [ ] Linux Build
- [ ] Setup script
