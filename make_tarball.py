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
    gapversion = get_makefile_var("GAP_BUILD_VERSION")
except:
    error("make sure GAP has been compiled via './configure && make'")
notice(f"Detected GAP version {gapversion}")

# Now set the variable tag. If only one tag points to the current
# commit, we use that tag. If more than one tag points to the current
# commit, the user has to provide the tag as an input to the script.
# If there is no tag, this is a nightly snapshot "release".
tags = subprocess.run(["git", "tag", "--points-at"],
                     check=True, capture_output=True, text=True)
tags = tags.stdout.strip().split('\n')
if len(sys.argv) == 2:
    provided_tag = sys.argv[1]
    if not provided_tag in tags:
        error(f"tag '{provided_tag}' does not point to the current commit")
    tag = provided_tag
elif len(tags) > 1:
    error("Current commit has more than one tag. Provide a tag as argument")
elif len(tags) == 1 and len(tags[0]) > 0:
    tag = tags[0]
else:
    tag = None

# Make sure tag is annotated and not lightweight.
# lightweight vs annotated
# https://stackoverflow.com/questions/40479712/how-can-i-tell-if-a-given-git-tag-is-annotated-or-lightweight#40499437
if tag != None:
    is_annotated = subprocess.run(["git", "for-each-ref", "refs/tags/" + tag],
                                  check=True, capture_output=True, text=True)
    is_annotated = "tag" == is_annotated.stdout.split()[1]
    if not is_annotated:
        error(tag + " must be an annotated tag and not lightweight")

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
    notice("removing unwanted files")
    shutil.rmtree("benchmark")
    shutil.rmtree("dev")
    shutil.rmtree(".github")
    for f in badfiles:
        try:
            os.remove(f)
        except:
            pass

    notice("patch configure.ac")
    patchfile("configure.ac", r"m4_define\(\[gap_version\],[^\n]+", r"m4_define([gap_version], ["+gapversion+"])")
    patchfile("configure.ac", r"m4_define\(\[gap_releaseday\],[^\n]+", r"m4_define([gap_releaseday], ["+commit_date+"])")
    patchfile("configure.ac", r"m4_define\(\[gap_releaseyear\],[^\n]+", r"m4_define([gap_releaseyear], ["+commit_year+"])")

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


# create the archives
with working_directory(tmpdir):
    filename = f"{basename}.tar.gz"
    notice(f"creating {filename}")
    shutil.make_archive(basename, 'gztar', ".", basename)
    with open(filename+".sha256", 'w') as file:
        file.write(sha256file(filename))

    filename = f"{basename}.zip"
    notice(f"creating {filename}")
    shutil.make_archive(basename, 'zip', ".", basename)
    with open(filename+".sha256", 'w') as file:
        file.write(sha256file(filename))

    notice("remove packages")
    shutil.rmtree(basename + "/pkg")

    filename = f"{basename}-core.tar.gz"
    notice(f"creating {filename}")
    shutil.make_archive(basename+"-core", 'gztar', ".", basename)
    with open(filename+".sha256", 'w') as file:
        file.write(sha256file(filename))

    filename = f"{basename}-core.zip"
    notice(f"creating {filename}")
    shutil.make_archive(basename+"-core", 'zip', ".", basename)
    with open(filename+".sha256", 'w') as file:
        file.write(sha256file(filename))


# The end
notice("DONE")
