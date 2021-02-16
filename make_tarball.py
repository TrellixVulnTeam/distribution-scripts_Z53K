#!/usr/bin/env python3
#
# This script is intended to implement step 4 of
# <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>, i.e.:
#
# 4. Create archives: run a script which takes a git ref (a sha1, a tag
# such  "v4.11.3") as argument. 


# TODO: maybe move this to the gap repository (say to `etc`), and let it
# work similarly to how ReleaseTools work:
#  - start it from the root dir of a clone of the gap-system/gap repository
#  - invoke it as `etc/make_release` (for nightlies) or `etc/make_release 4.X.Y`
#
# The script then does this:
#  - perhaps check that there are no uncommitted changes, like in ReleaseTools??
#  - (possibly store the release date somewhere?)
#  - if version given:
#    - check that version matches configure.ac
#    - `git fetch --tags`
#    - check if tag `v4.X.Y` already exists; if it does, warn / error
#      (could distinguish depending on whether the tag points to the right commit or not)
#  - download package tarballs
#    - CAVEAT: in the following we should use the packages in the tarball;
#      but we don't want to nuke the existing pkg dir. be mindful of this
#  - run `make doc`
#  - use `git archive` to put a snapshot of the repository into a separate dir
#  - cd into that new dir
#  - `autogen.sh`
#  - `./configure` (beware of complications due to dependencies / GMP / ...)
#  - `make && make doc`
#  - extract version from `cnf/GAP-VERSION-FILE`
#  - `make distclean` (after the relevant PRs have landed)
#  - ...
#  - if version was given:
#    - create annotated tag `v4.X.Y` via `git tag -m "Version 4.X.Y" v4.X.Y`
#    - push tag to github
#    - upload files to GitHub release: new tarballs and also package tarballs to 
#      to https://github.com/gap-system/gap/releases/tag/v4.X.Y
#      (see for example <https://github.com/gap-system/gap/releases/tag/v4.11.0>)
#  - if used on GitHub actions, the resulting files could be turned into "artifacts"
#    (Sergio knows how)

#from os import popen, path
import sys
#from sys import argv, exit, hexversion, stderr
#from zipfile import ZipFile
#import re
#import optparse
#import argparse
import subprocess

def notice(msg):
    print("\033[32m" + msg + "\033[0m")

def warning(msg):
    print("\033[33m" + msg + "\033[0m")

def error(msg):
    print("\033[31m" + msg + "\033[0m")
    sys.exit(1)


def download(url, dst):
    res = subprocess.call(["curl", "-C", "-", "-o", dst, url])
    if res != 0:
        print('failed downloading ' + url)
        sys.exit(1)





# Insist on Python 3
if sys.version_info < (3,0):
    error("Python 3.5 or newer is required")

if len(sys.argv) < 2 || len(sys.argv) > 3:
    print 'usage:', sys.argv[0], '<gitref> [packagetarball]'
    exit(1)

gitref = sys.argv[1]
if len(sys.argv) >= 3:
    packagetarball = sys.argv[2]
else:
    error("omitting packagetarball name not yet supported")
    # here is what we can do: if the gitref is a tag of the format v4.X.Y,
    # use that to derive the name of package tarball(s)
    # otherwise, use `git branch --contains SHA1` to determine the relevant
    #  branch (either the highest numbered stable-X.Y, else master/main)


print("")


# or maybe the package tarball should already be there, and its name specified as a second argument


#     - fetches the code from the given git ref in the GAP repository

print("TODO: invoke `git archive`") # or perhaps `git clone`

#     - fetches the versioned packages tarball

print("TODO: download package distro tarballs")
# TODO: also use existing tarballs if present, so that during retry on
# does not have to download again?
# TODO: add checksum validation?

#     - extracts packages in the code from git

print("TODO: extract package archive, either via Python package or by invoking `tar`")

pkgarchive = "https://github.com/gap-system/gap-distribution/releases/download/package-archives/packages-stable-4.11.tar.gz"
# TODO: for now use the above, in the future 

#     - run autogen.sh, configure

print("TODO: run autogen.sh") # needed anyway


print("TODO: run configure")  # needed for `make doc`
#  but beware: we must then also clean some of the files this produces



#     - build the GAP manual via `make doc`

print("TODO: run `make doc`")



#     - (possibly regenerates packages manuals as well???)
#     - remove LaTeX build artifacts

print("TODO: remove unwanted files")

# see <https://github.com/gap-system/gap-distribution/blob/master/DistributionUpdate/patternscolor.txt>
#
#   # files and directories we never include
#   -*.git/*
#   -*.DS_Store
#   # files we never include
#   -*.o
#   # excluded directories
#   -benchmark/*
#   -dev/*
#   #
#   # files and directories included in the main archive
#   #
#   +doc/ref/*
#   +doc/tut/*
#   +doc/hpc/*
#   +doc/gapmacro.tex
#   +doc/gapmacrodoc.tex
#   +doc/manualbib.xml
#   +doc/manualindex
#   +doc/make_doc.in
#   +doc/versiondata
#   +doc/versiondata.in
#   -doc/*
#   +etc/emacs/*
#   +etc/vim/*
#   +etc/convert.pl
#   -etc/*
#   # everything else is included
#   +*
#   

#     - run `tar`  to create `.tar.gz` (and perhaps also `.tar.xz`)

print("TODO: create tarballs from all")


# TODO: how to name the tarballs?
#  - gap-4.11.1.tar.gz  for branch v4.11.1 
#  - what do use for a random sha1? if we simply work in a git clone, we could
#    use the output of `git --version` (resp. parse `cnf/GAP-VERSION-FILE`)

# TODO: also create a gap-core-4.X.Y.tar.gz tarbll which omits the pkg dir
#  (but unlike the current one, perhaps it perhaps should contain the manual)

