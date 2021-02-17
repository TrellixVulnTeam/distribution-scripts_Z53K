#!/usr/bin/env python3

# This script is intended to implement step 3 of
# <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>, i.e.:
#
# 3. Upload current packages as "packages for 4.11.3"

import sys, subprocess
# If we do import * from utils, then initialize_github can't overwrite the
# global GITHUB_INSTANCE and CURRENT_REPO variables.
import utils

if len(sys.argv) != 2:
    raise Exception("usage : make_packages.py" \
                    + "<tag>")

TAG = sys.argv[1]
# TAG_NUMBER is TAG without the leading "v"
TAG_NUMBER = TAG[1:len(TAG)]
IS_MAJOR_RELEASE = (TAG[-1] == "0")

# TODO: where should we put this: initialize_github and create release on
# github
utils.initialize_github()

if utils.check_whether_github_release_exists(TAG):
    utils.error("Release " + TAG + " already exists!")
# TODO add notes. Also a CHANGES.md?
# From https://stackoverflow.com/questions/6245570/how-to-get-the-current-branch-name-in-git#12142066
CURRENT_BRANCH = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                text=True,
                                capture_output=True)
CURRENT_BRANCH = CURRENT_BRANCH.stdout.strip()
utils.CURRENT_REPO.create_git_release(TAG, TAG, "test message",
                                      target_commitish=CURRENT_BRANCH,
                                      prerelease=True)

URL_TO_PACKAGE_ARCHIVES = \
    "https://github.com/gap-system/gap-distribution/releases/download/package-archives/"

if IS_MAJOR_RELEASE:
    BRANCH = "master"
else:
    MAJOR_VERSION = TAG.split(".")[1]
    BRANCH = "stable-4." + MAJOR_VERSION

# TODO: do not download this again, if the tar ball already exists, but
# double-check that we're not using the wrong tar ball by accident.
# Download and rename the package tar balls:
# packages-master.tar.gz -> packages-4.11.0.tar.gz
# packages-required-master.tar.gz -> packages-required-4.11.0.tar.gz
PACKAGES_SRC = "packages-" + BRANCH + ".tar.gz"
PACKAGES_DST = "packages-" + TAG_NUMBER + ".tar.gz"
print("Downloading " + PACKAGES_SRC + " and renaming it to "
      + PACKAGES_DST)
# packages-stable-4.11.tar.gz -> packages-v4.11.1.tar.gz
# packages-required-stable-4.11.tar.gz -> packages-required-v4.11.1.tar.gz
utils.download(URL_TO_PACKAGE_ARCHIVES + PACKAGES_SRC,
               PACKAGES_DST)

PACKAGES_REQUIRED_SRC = "packages-required-" + BRANCH + ".tar.gz"
PACKAGES_REQUIRED_DST = "packages-required-" + TAG_NUMBER + ".tar.gz"
print("Downloading " + PACKAGES_REQUIRED_SRC + " and renaming it to "
      + PACKAGES_REQUIRED_DST)
utils.download(URL_TO_PACKAGE_ARCHIVES + PACKAGES_REQUIRED_SRC,
               PACKAGES_REQUIRED_DST)

# TODO: what happens if this crashes during the upload?
print("Uploading " + PACKAGES_DST + " and " + PACKAGES_REQUIRED_DST)
# --clobber means overwrite files with the same name
#subprocess.run("gh", "release", "upload", "--clobber",
#               TAG,
#               PACKAGES_DST,
#               PACKAGES_REQUIRED_DST,
#               check=True)
