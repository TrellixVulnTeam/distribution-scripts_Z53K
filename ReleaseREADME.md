# How To Make a GAP Release for version 4.X.Y
 
**This release process assumes the following**
- A stable branch of GAP has been identified or agreed upon. This branch will be identified here as `stable-4.X.Y` and the Release Notes in Changes.md have been created.
- You have a clone of the [GAP repository](https://github.com/gap-system/gap)
- You can compile this version of GAP (some dependencies for that are listed below, more might be need)
- You have a clone of the [GapWWW repository](https://github.com/gap-system/GapWWW)

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

1. Go into the gap-system/gap (repository) directory 
2. *Commit and tag release in git*
2. Run `make_packages.py` with the flag `v4.X.Y`
3. Run `make_tarball.py`
4. Change to the gap-system/GapWWW (repository) directory
5. Run `update_website.py` 

## Release Process -- The more detailed guide

1. Go into the gap-system/gap (repository) directory  
    This should be obvious why
2. *Commit and tag release in git*  
    *I am unsure now if this is still going to be done manually* 
2. Run `make_packages.py` with the flag `v4.X.Y`  
    This will pull the stable tar ball of packages from the archive, rename it to the right version and upload it to the right place in the gap repository.
3. Run `make_tarball.py`  
    - Fetches the stable version of GAP
    - Makes and configures GAP to check that it is indeed stable
    - Fetches the pkg tar ball
    - Builds the manuals
    - Cleans everything up
    - Builds the tar ball(s) and checksum files
    - Uploads the tar balls
4. Change to the gap-system/GapWWW (repository) directory  
   This should be obvious why
5. Run `update_website.py`   
    - 
