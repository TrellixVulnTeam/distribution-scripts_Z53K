#!/usr/bin/env python3
#
# This script is intended to implement step 7 of
# <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>, i.e.:
#
# 7. Update the website

#import subprocess
#import argparse
import sys
import requests
import datetime
import tempfile
import tarfile
from utils import *
from git import Repo

# Insist on Python >= 3.6 (perhaps this script doesn't need this...)
if sys.version_info < (3,6):
    error("Python 3.6 or newer is required")

# Verify that commands are available
verify_command_available("gh")
verify_command_available("git")
verify_command_available("tar")
verify_git_repo()
verify_git_clean()

#TODO Ensure we are on GapWWW repository
#TODO Ensure we are on master, up to date with origin/master pointing at the right place
#TODO git checkout -b NEW
# TODO can this be different for push and pull? TODO do this robustly!
#remote = subprocess.getoutput(["git config --get remote.origin.url"])
#GapWWW_remote = 'https://github.com/gap-system/GapWWW'
#if remote != GapWWW_remote:
#    error("origin remote must be " + GapWWW_remote)
#repo = Repo(os.getcwd())

# Calculate release date
today = datetime.datetime.today()
year = today.strftime('%Y')
date = today.strftime('%d %B %Y') # FIXME is this really the format that we want?
notice('release date will be ' + date)

# Query GitHub API over https to find the most recent release on gap-system/gap
github_releases = 'https://api.github.com/repos/gap-system/gap/releases'
request = requests.get(github_releases)
request.raise_for_status() # TODO better error handling
latest_release = request.json()[0] # dictionary with latest GitHub release info
# TODO don't necessarily assume that first release is the one we want

# Extract version number 4.X.Y and URL for gap-4.X.Y.tar.gz from the release dictionary
# Assert that the tag has the form v4.\d+.\d+
tag = latest_release['tag_name'].split('.')
assert(len(tag) == 3 and tag[0] == 'v4' and tag[1].isdigit() and tag[2].isdigit())
gap_version = latest_release['tag_name'][1:]
gap_version_major = tag[1]
gap_version_minor = tag[2]
notice('latest GAP release on github.com/gap-system/gap is ' + gap_version)

# Download the unique release asset named 'gap-4.X.Y.tar.gz'
tarball = 'gap-' + gap_version + '.tar.gz'
tarball_url = [ x['browser_download_url'] \
                for x in latest_release['assets'] \
                    if x['name'] == tarball ]
assert(len(tarball_url) == 1)
tarball_url = tarball_url[0]
#tmpdir = tempfile.gettempdir()
tmpdir = "/tmp/wilf_experiment/"
notice("tmpdir = " + tmpdir)
notice('downloading ' + tarball_url + ' to tmpdir')
download(tarball_url, tmpdir + tarball)

with working_directory(tmpdir):
    notice("extracting the GAP tarball to " + tmpdir)
    with tarfile.open(tarball) as tar:
        tar.extractall()
    os.remove(tarball)

gaproot = tmpdir + 'gap-' + gap_version + '/'
notice("Using GAP root " + gaproot)

# Compile GAP
with working_directory(gaproot):
    notice("running configure")
    with open("../configure.log", "w") as fp:
        subprocess.run(["./configure"], check=True, stdout=fp)

    notice("building GAP")
    with open("../make.log", "w") as fp:
        subprocess.run(["make"], check=True, stdout=fp)

notice("writing new _data/release.yml file")
with open('_data/release.yml', 'w') as release_yml:
    release_yml.write("# Release details concerning the most recently released GAP version\n")
    release_yml.write("# This file is automatically updated as part of the GAP release process\n")
    release_yml.write("version: '" + gap_version + "'\n")
    release_yml.write("date: '" + date + "'\n")
    release_yml.write("year: '" + year + "'\n")
print("TODO: git add _data/release.yml")

# FIXME Can we re-organise the website so that this is not necessary?
notice("appending \"gap4" + gap_version_major + \
       "dist: 'https://files.gap-system.org/gap-4." + gap_version_major + \
       "/'\" to _data/gap.yml, if necessary")
with open('_data/gap.yml', 'r+') as gap_yml:
    for line in gap_yml:
        if line.startswith("gap4" + gap_version_major + "dist:"):
            break
    else:
        gap_yml.write("gap4" + gap_version_major + \
                      "dist: 'https://files.gap-system.org/gap-4." + gap_version_major + "/'\n")
        print("TODO: git add _data/data.yml")

# i.e. run script which iterates over all packages and generates YAML files for each
notice("running etc/generate_package_yml_files_from_PackageInfo_files.sh")
subprocess.run(["etc/generate_package_yml_files_from_packageinfo_files.sh", gaproot], check=True)
print("TODO: git add _Packages/*.html")

notice("running GAP on etc/LinksOfAllHelpSections.g")
subprocess.run([gaproot + "bin/gap.sh", "-A", "etc/LinksOfAllHelpSections.g"], check=True)
print("TODO: git add _data/help.yml")

sys.exit(0)

# i.e. generate a YAML file with all required info about the release suitable for the NEW Jekyll based website
print("TODO: Create file _Releases/4." + ga-Pversion_major + "." + gap_version_minor + ".html for the new GAP version (or improve the setup here!)")
print("TODO: git add _Releases/4." + gap_version_major + "." + gap_version_minor + ".html")

print("TODO: git commit -m 'Update website for GAP '" + gap_version + " release'")
print("TODO: git push origin gap-" + gap_version )
print("TODO: create pull request")

# TODO Delete the temporary gap directory, when we are finished with it

# also commit and/or upload the GAP and GAP package manuals somewhere (HTML and PDF could go into different places)
# possibly helpful for inspiration:

#  https://github.com/BryanSchuetz/jekyll-deploy-gh-pages uses an GitHub Action to push to a branch
#  https://github.com/marketplace/actions/create-pull-request
