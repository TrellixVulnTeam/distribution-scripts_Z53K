# How To Make a GAP Release

## Dependencies
Before starting the release process, the scripts have the following dependencies. Make sure you have the following installed and up to date
- Python (version >=3.6) which can be installed using your favourite package manager or from [Python.org](https://www.python.org)
### Python Modules
The following (non-standard) python modules need to be installed, you can do this using `pip` (`pip install <MODULENAME>`)
- `PyGithub`
- `requests`
- `GitPython`

### Command line tools
The following command line tools are needed, please install them using your favourite package manager
- `curl`
- `git`
- `make`
- `autoconf`
- `gh`
- `tar`

## Release Process -- The quick guide

This release process assumes that a stable branch of GAP has been identified or agreed upon.
This branch will be identified here as `stable-4.X.Y`

1. Commit and tag release in git.
2. 

1. Create Actual release (and merge branch into master) on Gap-systems repo.

2. Move to gap-www repository to create PR to create release on webpage.


## Release Process -- The more detailed guide
