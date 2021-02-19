#!/usr/bin/env python3

# This script is intended to implement step 6 of
# <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>, i.e.
# it makes a github relase and uploads all tar balls as assets.
#
# The version of the gap release to be created can be provided as argument to
# this script and is handled as in make_tarball.py.

# If we do import * from utils, then initialize_github can't overwrite the
# global GITHUB_INSTANCE and CURRENT_REPO variables.
import utils
import github

try:
    GAPVERSION = get_makefile_var("GAP_BUILD_VERSION")
except:
    error("Could not get GAP version")
notice(f"Detected GAP version {GAPVERSION}")

utils.initialize_github()

if utils.check_whether_github_release_exists(GAPVERSION):
    utils.error(f"Release {GAPVERSION} already exists!")

CURRENT_BRANCH = get_makefile_var("PKG_BRANCH")
RELEASE_NOTE = f"For an overview of changes in GAP {GAPVERSION} see CHANGES.md file."
RELEASE = utils.CURRENT_REPO.create_git_release(TAG, TAG, RELEASE_NOTE,
                                      target_commitish=CURRENT_BRANCH,
                                      prerelease=True)

tmpdir = os.getcwd() + "/tmp"
with working_directory(tmpdir):
    manifest_filename = "__manifest_make_tarball"
    with open(manifest_filename, 'r') as manifest_file:
        manifest = manifest_file.read().splitlines()

# Upload all assets to release
try:
    for filename in manifest:
        utils.notice("Uploading " + filename)
        RELEASE.upload_asset(filename)
except github.GithubException:
    error("Error: The upload failed")
