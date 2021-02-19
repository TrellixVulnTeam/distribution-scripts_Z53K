#!/usr/bin/env python3

# This script is intended to implement step 6 of
# <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>, i.e.
# it makes a github relase and uploads all tar balls as assets.

import sys, subprocess
# If we do import * from utils, then initialize_github can't overwrite the
# global GITHUB_INSTANCE and CURRENT_REPO variables.
import utils
import github

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
CURRENT_BRANCH = get_makefile_var("PKG_BRANCH")
RELEASE = utils.CURRENT_REPO.create_git_release(TAG, TAG, "test message",
                                      target_commitish=CURRENT_BRANCH,
                                      prerelease=True)

if IS_MAJOR_RELEASE:
    BRANCH = "master"
else:
    MAJOR_VERSION = TAG.split(".")[1]
    BRANCH = "stable-4." + MAJOR_VERSION

PACKAGES_DST = "packages-" + TAG_NUMBER + ".tar.gz"
# packages-stable-4.11.tar.gz -> packages-v4.11.1.tar.gz
# packages-required-stable-4.11.tar.gz -> packages-required-v4.11.1.tar.gz
PACKAGES_REQUIRED_DST = "packages-required-" + TAG_NUMBER + ".tar.gz"

# Upload all assets to release
try:
    utils.notice("Uploading " + PACKAGES_DST)
    RELEASE.upload_asset(PACKAGES_DST)
except github.GithubException:
    error("Error: The upload failed")

# TODO: remove tmpdir that was created in make_tarball.py
