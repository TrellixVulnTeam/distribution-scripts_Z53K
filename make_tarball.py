#!/usr/bin/env python3
#
# This script is intended to implement step 4 of
# <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>, i.e.
# create the archives that form the gap release.

# The version of the gap release is taken from the Makefile variable
# GAP_BUILD_VERSION.

from utils import *

import shutil
import subprocess
import sys
import tarfile

# Insist on Python >= 3.6 for f-strings and other goodies
if sys.version_info < (3,6):
    error("Python 3.6 or newer is required")

notice("Checking prerequisites")
verify_command_available("curl")
verify_command_available("git")
verify_command_available("autoconf")
verify_command_available("make")
verify_git_repo()
verify_git_clean()

# fetch tags, so we can properly detect
safe_git_fetch_tags()

# Creating tmp directory
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

if gapversion.find("dev") == -1:
    notice(f"--- THIS LOOKS LIKE A RELEASE ---")
else:
    notice(f"--- THIS LOOKS LIKE A NIGHTLY BUILD ---")


# extract commit_date with format YYYY-MM-DD
commit_date = subprocess.run(["git", "show", "-s", "--format=%as"],
                             check=True, capture_output=True, text=True)
commit_date = commit_date.stdout.strip()
commit_year = commit_date[0:4]

# derive tarball names
basename = f"gap-{gapversion}"
all_packages = f"packages-v{gapversion}" # only the pkg dir
all_packages_tarball = f"{all_packages}.tar.gz"
req_packages = f"packages-required-v{gapversion}" # a subset of the above
req_packages_tarball = f"{req_packages}.tar.gz"

# Exporting repository content into tmp 
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
    
    import os
    
    def is_within_directory(directory, target):
        
        abs_directory = os.path.abspath(directory)
        abs_target = os.path.abspath(target)
    
        prefix = os.path.commonprefix([abs_directory, abs_target])
        
        return prefix == abs_directory
    
    def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
    
        for member in tar.getmembers():
            member_path = os.path.join(path, member.name)
            if not is_within_directory(path, member_path):
                raise Exception("Attempted Path Traversal in Tar File")
    
        tar.extractall(path, members, numeric_owner=numeric_owner) 
        
    
    safe_extract(tar, path=tmpdir)
os.remove(rawgap_tarfile)

# Cleaning things up
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

    # Building GAP
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

    # Downloading, building and extracting pkgs manuals
    notice("Downloading package tarballs")   # ... outside of the directory we just created
    download_with_sha256(PKG_BOOTSTRAP_URL+PKG_MINIMAL, "../"+req_packages_tarball)
    download_with_sha256(PKG_BOOTSTRAP_URL+PKG_FULL, "../"+all_packages_tarball)

    notice("Extract the packages")
    with tarfile.open("../"+all_packages_tarball) as tar:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, path="pkg")

    notice("Building the manuals")
    run_with_log(["make", "doc"], "gapdoc", "building the manuals")

    notice("Remove generated files we don't want for distribution")
    run_with_log(["make", "distclean"], "make-distclean", "make distclean")


# create the archives
# If you create additional archives, make sure to add them to archives_to_create!
archives_to_create = []
for filename in [all_packages, req_packages, basename, basename + "-core"]:
    archives_to_create.append(filename + ".tar.gz")
    archives_to_create.append(filename + ".tar.gz.sha256")
    archives_to_create.append(filename + ".zip")
    archives_to_create.append(filename + ".zip.sha256")

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

    filename = all_packages + '.zip'
    notice(f"Creating {filename}")
    shutil.make_archive(all_packages, 'zip', basename,  "pkg")
    with open(filename+".sha256", 'w') as file:
        file.write(sha256file(filename))

    notice("Extract required packages")
    with tarfile.open(req_packages_tarball) as tar:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, path=req_packages)

    filename = req_packages + '.zip'
    notice(f"Creating {filename}")
    shutil.make_archive(req_packages, 'zip', ".",  req_packages)
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

    manifest_filename = "__manifest_make_tarball"
    notice(f"Creating manifest {manifest_filename}")
    with open(manifest_filename, 'w') as manifest:
        for archive in archives_to_create:
            manifest.write(f"{archive}\n")

# The end
notice("DONE")
