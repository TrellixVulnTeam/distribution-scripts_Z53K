#!/usr/bin/env python3
#
# This script is intended to implement step 4 of
# <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>, i.e.
# create the archives that form the gap release.
#
# The version of the gap release to be created is taken to be the tag of the
# current commit or can be provided as argument to this script. If the current
# commit has no tag and no tag is provided as argument, then we create a
# "snapshot" release.

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
    error("usage: "+sys.argv[0]+" [<tag>]")

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
except FileExistsError:
    pass

# extract the GAP version from this directory *NOT THE SNAPSHOT DIR*
try:
    gapversion = get_makefile_var("GAP_BUILD_VERSION")
except:
    error("make sure GAP has been compiled via './configure && make'")
notice(f"Detected GAP version {gapversion}")

if gapversion.find("dev") = -1:
    notice(f"THIS LOOKS LIKE A RELEASE.")
else:
    notice(f"THIS LOOKS LIKE A NIGHTLY BUILD.")


# extract commit_date with format YYYY-MM-DD
commit_date = subprocess.run(["git", "show", "-s", "--format=%as"],
                             check=True, capture_output=True, text=True)
commit_date = commit_date.stdout.strip()
commit_year = commit_date[0:4]

# derive tarball names
basename = f"gap-{gapversion}"
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

with working_directory(tmpdir + "/" + basename):
    notice("Removing unwanted files")
    shutil.rmtree("benchmark")
    shutil.rmtree("dev")
    shutil.rmtree(".github")
    for f in badfiles:
        try:
            os.remove(f)
        except:
            pass

    # This sets the version, release day and year of the release we are
    # creating.
    notice("Patch configure.ac")
    patchfile("configure.ac", r"m4_define\(\[gap_version\],[^\n]+", r"m4_define([gap_version], ["+gapversion+"])")
    patchfile("configure.ac", r"m4_define\(\[gap_releaseday\],[^\n]+", r"m4_define([gap_releaseday], ["+commit_date+"])")
    patchfile("configure.ac", r"m4_define\(\[gap_releaseyear\],[^\n]+", r"m4_define([gap_releaseyear], ["+commit_year+"])")

    notice("Running autogen.sh")
    subprocess.run(["./autogen.sh"], check=True)

    notice("Running configure")
    run_with_log(["./configure"], "configure")

    notice("Building GAP")
    run_with_log(["make", "-j8"], "make")

    # extract some values from the build system
    branchname = get_makefile_var("PKG_BRANCH")
    PKG_BOOTSTRAP_URL = get_makefile_var("PKG_BOOTSTRAP_URL")
    PKG_MINIMAL = get_makefile_var("PKG_MINIMAL")
    PKG_FULL = get_makefile_var("PKG_FULL")
    notice(f"branchname = {branchname}")
    notice(f"PKG_BOOTSTRAP_URL = {PKG_BOOTSTRAP_URL}")
    notice(f"PKG_MINIMAL = {PKG_MINIMAL}")
    notice(f"PKG_FULL = {PKG_FULL}")

    notice("Downloading package tarballs")   # ... outside of the directory we just created
    download_with_sha256(PKG_BOOTSTRAP_URL+PKG_MINIMAL, "../"+req_packages_tarball)
    download_with_sha256(PKG_BOOTSTRAP_URL+PKG_FULL, "../"+all_packages_tarball)

    notice("Extract the packages")
    with tarfile.open("../"+all_packages_tarball) as tar:
        tar.extractall(path="pkg")

    notice("Building the manuals")
    run_with_log(["make", "doc"], "gapdoc", "building the manuals")

    notice("Remove generated files we don't want for distribution")
    run_with_log(["make", "distclean"], "make-distclean", "make distclean")


# create the archives
with working_directory(tmpdir):
    filename = f"{basename}.tar.gz"
    notice(f"Creating {filename}")
    shutil.make_archive(basename, 'gztar', ".", basename)
    with open(filename+".sha256", 'w') as file:
        file.write(sha256file(filename))

    filename = f"{basename}.zip"
    notice(f"Creating {filename}")
    shutil.make_archive(basename, 'zip', ".", basename)
    with open(filename+".sha256", 'w') as file:
        file.write(sha256file(filename))

    notice("Remove packages")
    shutil.rmtree(basename + "/pkg")

    filename = f"{basename}-core.tar.gz"
    notice(f"Creating {filename}")
    shutil.make_archive(basename+"-core", 'gztar', ".", basename)
    with open(filename+".sha256", 'w') as file:
        file.write(sha256file(filename))

    filename = f"{basename}-core.zip"
    notice(f"Creating {filename}")
    shutil.make_archive(basename+"-core", 'zip', ".", basename)
    with open(filename+".sha256", 'w') as file:
        file.write(sha256file(filename))


# The end
notice("DONE")
