#!/usr/bin/env python3

# This script is intended to implement step 4 of
# <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>, i.e.:
#
# 3. Upload current packages as "packages for 4.11.3"

import sys, urllib.request, subprocess

if len(sys.argv) != 2:
    raise Exception("usage : make_packages.py" \
                    + "<tag>")

TAG = sys.argv[1]
# TAG_NUMBER is TAG without the leading "v"
TAG_NUMBER = TAG[1:len(TAG)]
IS_MAJOR_RELEASE = (TAG[-1] == "0")

# TODO: this is a different step
# TODO add notes. Also a CHANGES.md?
subprocess.run("gh release create " + TAG
               + " --prerelease"
               + " --title " + TAG
               + " --notes \"test notes\"",
               shell=True)

URL_TO_PACKAGE_ARCHIVES = \
    "https://github.com/gap-system/gap-distribution/releases/download/package-archives/"

if IS_MAJOR_RELEASE:
    BRANCH = "master"
else:
    MAJOR_VERSION = TAG.split(".")[1]
    BRANCH = "stable-4." + MAJOR_VERSION

# Download and rename the package tar balls:
# packages-master.tar.gz -> packages-4.11.0.tar.gz
# packages-required-master.tar.gz -> packages-required-4.11.0.tar.gz
PACKAGES_SRC = "packages-" + BRANCH + ".tar.gz"
PACKAGES_DST = "packages-" + TAG_NUMBER + ".tar.gz"
print("Downloading " + PACKAGES_SRC + " and renaming it to "
      + PACKAGES_DST)
# packages-stable-4.11.tar.gz -> packages-v4.11.1.tar.gz
# packages-required-stable-4.11.tar.gz -> packages-required-v4.11.1.tar.gz
urllib.request.urlretrieve(URL_TO_PACKAGE_ARCHIVES + PACKAGES_SRC,
                           PACKAGES_DST)

PACKAGES_REQUIRED_SRC = "packages-required-" + BRANCH + ".tar.gz"
PACKAGES_REQUIRED_DST = "packages-required-" + TAG_NUMBER + ".tar.gz"
print("Downloading " + PACKAGES_REQUIRED_SRC + " and renaming it to "
      + PACKAGES_REQUIRED_DST)
urllib.request.urlretrieve(URL_TO_PACKAGE_ARCHIVES + PACKAGES_REQUIRED_SRC,
                           PACKAGES_REQUIRED_DST)

print("Uploading " + PACKAGES_DST + " and " + PACKAGES_REQUIRED_DST)
subprocess.run("gh release upload --clobber " + TAG
               + " " + PACKAGES_DST
               + " " + PACKAGES_REQUIRED_DST,
               shell=True)
