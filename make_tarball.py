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
#from sys import argv, exit, hexversion, stderr
#from zipfile import ZipFile
#import re
#import optparse
#import argparse

from utils import *

import shutil
import subprocess
import sys
import tarfile
import tempfile

# Insist on Python >= 3.6 for f-strings and other goodies
if sys.version_info < (3,6):
    error("Python 3.6 or newer is required")

# if len(sys.argv) < 2 or len(sys.argv) > 3:
#     error('usage: ' + sys.argv[0] + ' <gitref> [packagetarball]')
#
# # TODO: make the gitref optional? then use the current HEAD commit
# # How do we figured out if it refers to a versioned release? well
# # either check if there is a v4.X.Y tag pointing to HEAD, OR just say
# # that this mode of operation is not supported?
# # Another option is to have a flag to select between "nightly release"
# # and "proper release"???
# #
# # Let's see, here are two hypothetical invocations and what could happen:
# #
# #  $ ./make_tarball.py
# #  The version set in configure.ac is 4.X.Y; using existing tag v4.X.Y
# #  ....
# #
# #  $ ./make_tarball.py
# #  The version set in configure.ac is 4.X.Y; shall I create and use a tag v4.X.Y? (Y/n)
# #  ....
# #
# #  $ ./make_tarball.py --nightly
# #  The version set in configure.ac is 4.X.Y; continuing in nightly mode
# #  ....
# gitref = sys.argv[1]
# if len(gitref) <= 2:
#     error(f"gitref {gitref} is too short")
#
# # TODO: verify the
#
# if all(c in string.hexdigits for c in s) and len(s) <= 20:
#     # look like a sha1ref
#     is_version_ref = False
# elif:
#     pass
# else:
#     error("unsupported gitref")
#
# if len(sys.argv) >= 3:
#     packagetarball = sys.argv[2]
# else:
#     error("omitting packagetarball name not yet supported")
#     # TODO: we could do this: if the gitref is a tag of the format v4.X.Y,
#     # use that to derive the name of package tarball(s)
#     # otherwise, use `git branch --contains SHA1` to determine the relevant
#     # branch (either the highest numbered stable-X.Y, else master/main)
#

notice("Checking prerequisites")
verify_command_available("curl")
verify_command_available("git")
verify_command_available("autoconf")
verify_command_available("make")
verify_git_repo()
verify_git_clean()

# fetch tags, so we can properly detect
subprocess.run(["git", "fetch", "--tags"], check=True)

# ensure that everyt


# make print-PKG_BRANCH
gapversion = "4.X.Y" # TODO: extract this from


basename = f"gap-{gapversion}" # TODO/FIXME insert proper name
#with tempfile.TemporaryDirectory() as tmpdir:
tmpdir = "/tmp/foobar"
notice(f"tmpdir = {tmpdir}")

notice("Exporting repository content via `git archive`")
rawgap_tarfile = f"{tmpdir}/{basename}.tar"
subprocess.run(["git", "archive",
                f"--prefix={basename}/",
                f"--output={rawgap_tarfile}",
                "HEAD"], check=True)

notice("Extracting exported content")

with tarfile.open(rawgap_tarfile) as tar:
    tar.extractall(path=tmpdir)

os.remove(rawgap_tarfile)


badfiles = [
".appveyor.yml",
".codecov.yml",
".gitattributes",
".gitignore",
".mailmap",
".travis.yml",
]

with working_directory(tmpdir + "/" + basename):
    # remove a bunch of files
    shutil.rmtree("benchmark")
    shutil.rmtree("dev")
    shutil.rmtree(".github")
    for f in badfiles:
        try:
            os.remove(f)
        except:
            pass

    # build GAP
    subprocess.run(["./autogen.sh"], check=True)
    subprocess.run(["./configure"], check=True)
    #subprocess.run(["make", "-j8"], check=True) # FIXME: currently broken on gap master, fix already submitted
    subprocess.run(["make"], check=True)
    
    # get required packages tarball
    subprocess.run(["make", "bootstrap-pkg-minimal"], check=True) # FIXME
    rmtree
    #subprocess.run(["make", "bootstrap-pkg-full"], check=True)
    subprocess.run(["make", "doc"], check=True)

    # remove generated files we don't want for distribution
    subprocess.run(["make", "distclean"], check=True)


# Now create the tarball
main_tarball = f"{basename}.tar.gz"
core_tarball = f"{basename}-core.tar.gz" # same as above but without pkg dir
all_packages_tarball = f"packages-v{gapversion}.tar.gz" # only the pkg dir
req_packages_tarball = f"packages-required-v{gapversion}.tar.gz" # a subset of the above

with working_directory(tmpdir):
    with tarfile.open(main_tarball, "w:gz") as tar:
        tar.add(basename)

    with tarfile.open(all_packages_tarball, "w:gz") as tar:
        tar.add(basename + "/pkg")

    #TODO: get the required tarball out there?
    #with tarfile.open(req_packages_tarball, "w:gz") as tar:
    #    tar.add(basename + "/pkg")

#     - fetches the versioned packages tarball

print("TODO: download package distro tarballs")
# TODO: also use existing tarballs if present, so that during retry on
# does not have to download again?
# TODO: add checksum validation?

#     - extracts packages in the code from git

print("TODO: extract package archive, either via Python package or by invoking `tar`")

pkgarchive = "https://github.com/gap-system/gap-distribution/releases/download/package-archives/packages-stable-4.11.tar.gz"
# TODO: for now use the above, in the future

#     - run `tar`  to create `.tar.gz` (and perhaps also `.tar.xz`)

print("TODO: create tarballs from all")


# TODO: how to name the tarballs?
#  - gap-4.11.1.tar.gz  for branch v4.11.1
#  - what do use for a random sha1? if we simply work in a git clone, we could
#    use the output of `git --version` (resp. parse `cnf/GAP-VERSION-FILE`)

# TODO: also create a gap-core-4.X.Y.tar.gz tarball which omits the pkg dir
#  (but unlike the current one, perhaps it perhaps should contain the manual)


# The end
notice("DONE")
