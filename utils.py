import contextlib
import os
import shutil
import subprocess
import sys
from getpass import getpass
import github

CURRENT_REPO_NAME = "fingolfin/distribution-scripts"
# Initialized by initialize_github
GITHUB_INSTANCE = None
CURRENT_REPO = None

# print notices in green
def notice(msg):
    print("\033[32m" + msg + "\033[0m")

# print warnings in yellow
def warning(msg):
    print("\033[33m" + msg + "\033[0m")

# print error in red and exit
def error(msg):
    print("\033[31m" + msg + "\033[0m")
    sys.exit(1)

def verify_command_available(cmd):
    if shutil.which(cmd) == None:
        error(f"the '{cmd}' command was not found, please install it")
    # TODO: do the analog of this in ReleaseTools bash script:
    # command -v curl >/dev/null 2>&1 ||
    #     error "the 'curl' command was not found, please install it"

def verify_git_repo():
    res = subprocess.run(["git", "--git-dir=.git", "rev-parse"], stderr = subprocess.DEVNULL)
    if res.returncode != 0:
        error("current directory is not a git root directory")

# check for uncommitted changes
def verify_git_clean():
    res = subprocess.run(["git", "update-index", "--refresh"])
    if res.returncode == 0:
        res = subprocess.run(["git", "diff-index", "--quiet", "HEAD", "--"])
    if res.returncode != 0:
        error("uncommitted changes detected")

# from https://code.activestate.com/recipes/576620-changedirectory-context-manager/
@contextlib.contextmanager
def working_directory(path):
    """A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.

    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)

# helper for extracting values of variables set in the GAP Makefiles.rules
def get_makefile_var(var):
    res = subprocess.run(["make", f"print-{var}"], check=True, capture_output=True)
    kv = res.stdout.decode('ascii').strip().split('=')
    assert len(kv) == 2
    assert kv[0] == var
    return kv[1]

# download file at the given URL to path `dst`
# TODO: check at startup if `curl is present`
def download(url, dst):
    res = subprocess.run(["curl", "-L", "-C", "-", "-o", dst, url])
    if res.returncode != 0:
        error('failed downloading ' + url)

# Returns a boolean
def check_whether_git_tag_exists(tag):
    subprocess.run(["git", "fetch", "--tags"])
    res = subprocess.run(["git", "tag", "-l"],
                         capture_output=True,
                         text=True,
                         check=True)
    tags = res.stdout.split('\n')
    for s in tags:
        if tag == s:
            return True
    return False

# Returns a boolean
def check_whether_github_release_exists(tag):
    if CURRENT_REPO == None:
        print("CURRENT_REPO is not initialized. Call initialize_github first")
    releases = CURRENT_REPO.get_releases()
    for release in releases:
        if release.tag_name == tag:
            return True
    return False

# sets the global variables GITHUB_INSTANCE and CURRENT_REPO
def initialize_github(token=None):
    global GITHUB_INSTANCE, CURRENT_REPO
    #TODO: error if global variables already bound?
    if token == None and "GITHUB_TOKEN" in os.environ:
        token = os.environ["GITHUB_TOKEN"]
    if token == None:
        while True:
            name = input("Username for 'https://github.com': ")
            password = getpass("Password for " + name + ": ")
            g = github.Github(name, password)
            try:
                g.get_user().name
            except github.GithubException:
                print("Can't access GitHub: maybe the password is incorrect?")
                continue
    else:
        g = github.Github(token)
        try:
            g.get_user().name
        except github.GithubException:
            error("Error: the access token may be incorrect")
    GITHUB_INSTANCE = g
    CURRENT_REPO = GITHUB_INSTANCE.get_repo(CURRENT_REPO_NAME)
