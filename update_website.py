#!/usr/bin/env python3
#
# This script is intended to implement step 7 of
# <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>, i.e.:
#
# 7. Update the website

import subprocess
import sys
#import make_tarball

print("TODO: Get the gaproot of the GAP we want to load later")
gap_executable = '~/gap/bin/gap.sh'

print("TODO: Get the gaproot of packages whose PackageInfo.g files we want to convert to YAML")
gaproot_for_pkgs = '~/gap'

print("TODO: Get the new GAP release version and date from wherever")
version = '4.11.1'
version_major = version.split('.')[1]
version_minor = version.split('.')[2]
date = '32 February 2999' # FIXME is this the format we want?
year = '2999'             # TODO work out year from date?

print("TODO: Change directory to the GapWWW repository")
print("TODO: Ensure we are on a clean master, up to date with origin/master")
print("TODO: git checkout -b gap-" + version)

print("Writing new _data/release.yml... file with new GAP version, date, year")
with open('_data/release.yml', 'w') as release_yml:
    release_yml.write("# Release details concerning the most recently released GAP version\n")
    release_yml.write("# This file is automatically updated as part of the GAP release process\n")
    release_yml.write("version: '" + version + "'\n")
    release_yml.write("date:    '" + date + "'\n")
    release_yml.write("year:    '" + year + "'\n")
print("TODO: git add _data/release.yml")

# FIXME this doesn't feel like a great thing to be doing
print("TODO: Possibly append \"gap4" + version_major + \
      "dist: 'https://files.gap-system.org/gap-4." + version_major + "/'\" to _data/gap.yml")
if version_minor == '0': # FIXME: better check for whether this is necessary. Hopefully it should never be necessary.
    with open('_data/gap.yml', 'a') as gap_yml:
        gap_yml.write("gap4" + version_major + "dist: 'TODO'")
    print("TODO: git add _data/data.yml")

print("TODO: run etc/generate_package_yml_files_from_PackageInfo_files.sh <gaproot_for_pkgs>")
# i.e. run script which iterates over all packages and generates YAML files for each
print("TODO: git add _Packages/*.html")

print("TODO: Create file _Releases/4." + version_major + "." + version_minor + ".html for the new GAP version (or improve the setup here!)")
# i.e. generate a YAML file with all required info about the release suitable for the NEW Jekyll based website

print("TODO: git add _Releases/4." + version_major + "." + version_minor + ".html")

print("TODO: git commit -m 'Update website for GAP '" + version + " release'")
print("TODO: git push origin gap-" + version )
print("TODO: create pull request")

# also commit and/or upload the GAP and GAP package manuals somewhere (HTML and PDF could go into different places)
# possibly helpful for inspiration:

#  https://github.com/BryanSchuetz/jekyll-deploy-gh-pages uses an GitHub Action to push to a branch
#  https://github.com/marketplace/actions/create-pull-request
