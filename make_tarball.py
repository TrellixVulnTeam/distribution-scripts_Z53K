#!/usr/bin/env python3
#
# This script is intended to implement step 4 of
# <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>, i.e.:
#
# 4. Create archives: run a script which takes a git ref (a sha1, a tag
# such  "v4.11.3") as argument.

from utils import *

import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

# Insist on Python >= 3.6 for f-strings and other goodies
if sys.version_info < (3,6):
    error("Python 3.6 or newer is required")

if len(sys.argv) > 2:
    error("usage : make_packages.py [<tag>]")

notice("Checking prerequisites")
verify_command_available("curl")
verify_command_available("git")
verify_command_available("autoconf")
verify_command_available("make")
verify_git_repo()
verify_git_clean()

# fetch tags, so we can properly detect
safe_git_fetch_tags()


tmpdir = os.getcwd() + "/tmp"
notice(f"Files will be put in {tmpdir}")
try:
    os.mkdir(tmpdir)
except:
    pass

# extract the GAP version from this directory *NOT THE SNAPSHOT DIR*
try:
    subprocess.run(["make", "cnf/GAP-VERSION-FILE"], check=True, capture_output=True)
except:
    error("make sure GAP has been compiled via './configure && make'")
gapversion = open("cnf/GAP-VERSION-FILE").readlines()[0].split('=')[1].strip()
notice(f"Detected GAP version {gapversion}")

# Now set the variable tag. If only one tag points to the current commit, we
# use that tag. If more than one tag points to the current commit. In that
# case, the user has to provide the tag as an input to the script.
tags = subprocess.run(["git", "tag", "--points-at"],
                     check=True, capture_output=True, text=True)
tags = tags.strip().split('\n')
provided_tag = None
if len(sys.argv) = 2:
    provided_tag = sys.argv[1]
if provided_tag == None:
    if len(tags) > 1:
        error("Current commit has more than one tag. Provide a tag as argument")
    tag = tags[0]
else:
    if not provided_tag in tags:
        error("<tag> does not point to the current commit")
    tag = provided_tag

# Make sure tag is annotated and not lightweight.
# lightweight vs annotated
# https://stackoverflow.com/questions/40479712/how-can-i-tell-if-a-given-git-tag-is-annotated-or-lightweight#40499437
is_annotated = subprocess.run(["git", "for-each-ref", "refs/tags/" + tag],
                              check=True, capture_output=True, text=True)
is_annotated = "tag" == is_annotated.stdout.split()[1]
if not is_annotated:
    error(tag + " must be an annotated tag and not lightweight")

# TODO
# write the following info into configure.ac
# - version
# - release day
# - release year
# commit_date is of format YYYY-MM-DD
commit_date = subprocess.run(["git", "show", "-s", "--format=%as"],
                             check=True, capture_output=True, text=True)
commit_date = commit_date.stdout.strip()


# derive tarball names
basename = f"gap-{gapversion}"
main_tarball = f"{basename}.tar.gz"
main_zip = f"{basename}.zip"
core_tarball = f"{basename}-core.tar.gz" # same as above but without pkg dir
core_zip = f"{basename}-core.zip"
all_packages_tarball = f"packages-v{gapversion}.tar.gz" # only the pkg dir
req_packages_tarball = f"packages-required-v{gapversion}.tar.gz" # a subset of the above


notice("Exporting repository content via `git archive`")
rawbasename = "gap-raw"
rawgap_tarfile = f"{tmpdir}/{rawbasename}.tar"
subprocess.run(["git", "archive",
                f"--prefix={basename}/",
                f"--output={rawgap_tarfile}",
                "HEAD"], check=True)

notice("Extracting exported content")
shutil.rmtree(basename, ignore_errors=True) # remove any leftovers
with tarfile.open(rawgap_tarfile) as tar:
    tar.extractall(path=tmpdir)
os.remove(rawgap_tarfile)


notice("Processing exported content")

badfiles = [
".appveyor.yml",
".codecov.yml",
".gitattributes",
".gitignore",
".mailmap",
".travis.yml",
]

# TODO: patch configure.ac, insert right date/year/version here:
# m4_define([gap_version], [4.12dev])
# m4_define([gap_releaseday], [today])
# m4_define([gap_releaseyear], [this year])

with working_directory(tmpdir + "/" + basename):
    notice("removing unwanted files")
    shutil.rmtree("benchmark")
    shutil.rmtree("dev")
    shutil.rmtree(".github")
    for f in badfiles:
        try:
            os.remove(f)
        except:
            pass

    notice("running autogen.sh")
    subprocess.run(["./autogen.sh"], check=True)

    notice("running configure")
    with open("../configure.log", "w") as fp:
        subprocess.run(["./configure"], check=True, stdout=fp)

    notice("building GAP")
    with open("../make.log", "w") as fp:
        #subprocess.run(["make", "-j8"], check=True, stdout=fp) # FIXME: currently broken on gap master, fix already submitted
        subprocess.run(["make"], check=True, stdout=fp)

    # extract some values from the build system
    branchname = get_makefile_var("PKG_BRANCH")
    PKG_BOOTSTRAP_URL = get_makefile_var("PKG_BOOTSTRAP_URL")
    PKG_MINIMAL = get_makefile_var("PKG_MINIMAL")
    PKG_FULL = get_makefile_var("PKG_FULL")
    notice(f"branchname = {branchname}")
    notice(f"PKG_BOOTSTRAP_URL = {PKG_BOOTSTRAP_URL}")
    notice(f"PKG_MINIMAL = {PKG_MINIMAL}")
    notice(f"PKG_FULL = {PKG_FULL}")

    notice("downloading package tarballs")   # ... outside of the directory we just created
    download_with_sha256(PKG_BOOTSTRAP_URL+PKG_MINIMAL, "../"+req_packages_tarball)
    download_with_sha256(PKG_BOOTSTRAP_URL+PKG_FULL, "../"+all_packages_tarball)

    notice("extract the packages")
    with tarfile.open("../"+all_packages_tarball) as tar:
        tar.extractall(path="pkg")

    notice("building the manuals")
    with open("../gapdoc.log", "w") as fp:
        subprocess.run(["make", "doc"], check=True, stdout=fp)

    notice("remove generated files we don't want for distribution")
    subprocess.run(["make", "distclean"], check=True, capture_output=True)


with working_directory(tmpdir):
    notice(f"creating {main_tarball}")
    with tarfile.open(main_tarball, "w:gz") as tar:
        tar.add(basename)

    notice(f"creating {main_zip}")
    shutil.make_archive(main_zip[0:-4], 'zip', basename)

    notice(f"creating {core_tarball}")
    shutil.rmtree(basename + "/pkg")
    with tarfile.open(core_tarball, "w:gz") as tar:
        tar.add(basename)

    notice(f"creating {core_zip}")
    shutil.make_archive(core_zip[0:-4], 'zip', basename)


# TODO: also create .tar.bz2, .tar.xz (?), .zip (Python should be able to deal with all of them)

# TODO: also create sha256 checksum files for everything, using sha256file() in utils.py

# The end
notice("DONE")
