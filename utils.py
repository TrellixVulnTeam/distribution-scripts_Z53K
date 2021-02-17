import contextlib
import os
import shutil
import subprocess
import sys
from getpass import getpass
import github

CURRENT_REPO = "fingolfin/distribution-scripts"

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
    res = subprocess.run(["curl", "-L", "-C", "-", "-z", dst, "-o", dst, url])
    if res.returncode != 0:
        error('failed downloading ' + url)

# Returns a boolean
def check_whether_git_tag_exists(tag):
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
def check_whether_github_release_exists(github_instance, tag):
    repo = github_instance.get_repo(CURRENT_REPO)
    releases = repo.get_releases()
    for release in releases:
        if release.tag_name == tag:
            return True
    return False

def create_github_instance(token=None):
    while True:
        if token == None:
            name = input("Username for 'https://github.com': ")
            password = getpass("Password for 'https://"+name+"@github.com': ")
            g = github.Github(name, password)
        else:
            g = github.Github(token)
        try:
            g.get_user().name
        except:
            continue
        return g
