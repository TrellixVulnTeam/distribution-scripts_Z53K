#!/usr/bin/env python3
#
# This script is intended to implement step 7 of
# <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>, i.e.:
#
# 7. Update the website

# FIXME standardise on single or double quotes for strings

#import subprocess
#import argparse
import sys
import requests
import datetime
import tempfile
import tarfile
from utils import *
from git import Repo

def is_possible_gap4_release_tag(tag):
    tag = tag.split('.')
    return len(tag) == 3 and tag[0] == 'v4' and all(x.isdigit() for x in tag[1:])

def mb_bytes(nrbytes):
    return str(round(int(nrbytes) / (1024 * 1024)))

# Verify the necessary pre-requisites

# Insist on Python >= 3.6
if sys.version_info < (3,6):
    error("Python 3.6 or newer is required")

# Verify that commands are available
verify_command_available("gh")
verify_command_available("git")
verify_command_available("tar")
verify_git_repo()
verify_git_clean()


# TODO Process arguments, including a -h, --help describing the script

# TODO Add optional argument: name of remote to push to (default: origin)
remote = 'origin'

# TODO Add optional argument: git_tag of the release (default: '', to use the latest release)
# TODO I am still implicitly assuming that the tag is
release_name = ''
assert(release_name == '' or is_possible_gap4_release_tag(release_name))

# TODO Ensure we are in GapWWW repository
# TODO Ensure we are on master, up to date with origin/master pointing at the right place
# TODO git checkout -b NEW
# TODO can this be different for push and pull?
# TODO do this robustly!
# TODO allow this to be git@github.com:gap-system/GapWWW.git too
GapWWW_remotes = [ 'https://github.com/gap-system/GapWWW',\
                   'git@github.com:gap-system/GapWWW.git' ]
remote_url = subprocess.getoutput(["git config --get remote." + remote + ".url"])
if remote_url[-1] == '/':
    remote_url = remote_url[:-1]
if not remote_url in GapWWW_remotes:
    error("the remote '" + remote + "' must point to one of " + str(GapWWW_remotes) + \
            " (not " + remote_url+ ")")
#repo = Repo(os.getcwd())

# Calculate release date
today = datetime.datetime.today()
year = today.strftime('%Y')
month = today.strftime('%B')
date = today.strftime('%d %B %Y') # FIXME is this really the format that we want?
notice('release date will be ' + date)

# Query GitHub API over https to find the most recent release on gap-system/gap
# TODO Do this via PyGitHub?
github_releases_url = 'https://api.github.com/repos/gap-system/gap/releases'
request = requests.get(github_releases_url)
request.raise_for_status() # TODO better error handling
github_releases = request.json() # dictionary with latest GitHub release info
if release_name == '':
    release = github_releases[0]
else:
    release = [ x for x in github_releases if x['tag_name'] == release_name ]
    if len(release) != 1:
        error("non-existent or amnbiguous release tag name " + release_nane)
    release = release[0]

# Extract version number 4.X.Y and URL for gap-4.X.Y.tar.gz from the release dictionary
# Assert that the tag has the form v4.\d+.\d+
assert(is_possible_gap4_release_tag(release['tag_name']))
gap_version = release['tag_name'][1:]
tag = gap_version.split('.')
gap_version_major = tag[1]
gap_version_minor = tag[2]
notice('Requested GAP release on github.com/gap-system/gap is ' + gap_version)

# Download the unique release asset named 'gap-4.X.Y.tar.gz'
tarball = 'gap-' + gap_version + '.tar.gz'
tarball_url = [ x['browser_download_url'] \
                for x in release['assets'] if x['name'] == tarball ]
assert(len(tarball_url) == 1)
tarball_url = tarball_url[0]
#tmpdir = tempfile.gettempdir()
tmpdir = "/tmp/wilf_experiment/"
notice("tmpdir = " + tmpdir)
notice('downloading ' + tarball_url + ' to tmpdir')
#download(tarball_url, tmpdir + tarball)

with working_directory(tmpdir):
    notice("extracting the GAP tarball to " + tmpdir)
    #with tarfile.open(tarball) as tar:
    #    tar.extractall()
    #os.remove(tarball)

gaproot = tmpdir + 'gap-' + gap_version + '/'
notice("Using GAP root " + gaproot)

# Compile GAP
with working_directory(gaproot):
    notice("running configure")
    #with open("../configure.log", "w") as fp:
    #    subprocess.run(["./configure"], check=True, stdout=fp)

    notice("building GAP")
    #with open("../make.log", "w") as fp:
    #    subprocess.run(["make"], check=True, stdout=fp)

notice("writing new _data/release.yml file")
with open('_data/release.yml', 'w') as release_yml:
    release_yml.write("# Release details concerning the most recently released GAP version\n")
    release_yml.write("# This file is automatically updated as part of the GAP release process\n")
    release_yml.write("version: '" + gap_version + "'\n")
    release_yml.write("date: '" + date + "'\n")
    release_yml.write("year: '" + year + "'\n")
subprocess.run(["git", "add", "_data/release.yml"], check=True)

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
        subprocess.run(["git", "add", "_data/data.yml"], check=True)

# i.e. run script which iterates over all packages and generates YAML files for each
notice("running etc/generate_package_yml_files_from_PackageInfo_files.sh")
subprocess.run(["etc/generate_package_yml_files_from_packageinfo_files.sh", gaproot], check=True)
subprocess.run(["git", "add", "_Packages/*.html"], check=True)

notice("running GAP on etc/LinksOfAllHelpSections.g")
subprocess.run([gaproot + "bin/gap.sh", "-A", "-r", "-q", "etc/LinksOfAllHelpSections.g"], check=True)
subprocess.run(["git", "add", "_data/help.yml"], check=True)


################################################################################
# Build the new file _Releases/4.X.Y.html required by the Jekyll based website
# i.e. generate a YAML file with all required info about the release suitable for the NEW Jekyll based website
release_file = "_Releases/" + gap_version + ".html"
notice("writing a new release file: " + release_file)

with open(release_file, 'w') as new_file:
    new_file.write("---\n")
    new_file.write("version: " + gap_version + "\n")
    new_file.write('date: "' + month + ' ' + year + '"\n')
    new_file.write("packages:")

# Insert brief YAML data describing each package included in this GAP release
notice("running etc/new.sh")
subprocess.run(["etc/new.sh", gaproot, release_file], check=True)

with open(release_file, 'a') as new_file:
    new_file.write("""
---

<h2>Linux and OS X</h2>

<p>
Download one of the archives below, unpack it and run <code>./configure &amp;&amp; make</code>
in the unpacked directory. Then change to the <code>pkg</code> subdirectory and call
<code>../bin/BuildPackages.sh</code> to run the script which will build most of the
packages that require compilation (provided sufficiently many libraries, headers and
tools are available). For further details, see <a href="../Download/index.html">here</a>.
Expert users can find the description of all installation options in the
<a href="https://github.com/gap-system/gap/blob/v{{page.version}}/INSTALL.md">INSTALL.md</a> file.
</p>

<table>
 <colgroup>
  <col width="30%">
  <col width="20%">
  <col width="50%">
 </colgroup>""")
    for asset in release['assets']:
        if asset['name'].startswith('gap-' + gap_version + '.'):
            new_file.write('\n<tr>\n')
            new_file.write('  <td align="left"><a href="' + asset['browser_download_url'] + '">' + asset['name'] + '</a></td>\n')
            new_file.write('  <td align="left">' + MB_bytes(asset['size']) + ' MB</td>\n')
            # TODO download the asset and compute the sha256 checksum and put it
            # in the following cell, in the format "sha256: <checksum>"
            new_file.write('  <td align="left"></td>\n')
            new_file.write('</tr>')
    new_file.write("""
</table>
<p>
You may also consider one of the
<a href="../Download/alternatives.html">alternative distributions</a>.
Note, however, that these are updated independently and may not yet
provide the latest GAP release.
</p>""")
    new_file.write("""
<h2>Packages included in this release</h2>

<p>
Each of the GAP {{page.version}} archives contains 
the core GAP system (the source code,
<a href="../Datalib/datalib.html">data libraries</a>, regression tests and 
<a href="../Doc/manuals.html">documentation</a>), and the following selection of
<a href="../Packages/packages.html">packages</a>:
</p>
""")
subprocess.run(["git", "add", release_file], check=True)


################################################################################
# Create pull request to github.com/gap-system/GapWWW
# TODO Add option --force
subprocess.run(["git", "checkout", "-b", "gap-" + gap_version], check=True)
subprocess.run(["git", "commit", "-m", "'Update website for GAP " + gap_version + " release'"], check=True)
print("TODO: git push origin gap-" + gap_version )
print("TODO: create pull request")

sys.exit(0)

# TODO Delete the temporary gap directory, when we are finished with it
# TODO Download all package tarballs, and compute their sizes and sha256 checksums
# TODO stfp tarballs from GitHub release system to gap-system.org
# sftp gap-web@gap-web.host.cs.st-andrews.ac.uk
# cd files.gap-system.org

# also commit and/or upload the GAP and GAP package manuals somewhere (HTML and PDF could go into different places)
# possibly helpful for inspiration:

#  https://github.com/BryanSchuetz/jekyll-deploy-gh-pages uses an GitHub Action to push to a branch
#  https://github.com/marketplace/actions/create-pull-reques
