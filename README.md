# distribution-scripts

This repository contains work towards implementing the plan outlined
in <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>.

We will use Python >= 3.5, as it is more powerful than shell scripts,
and arguably more portable. It also offers packages for many things.

For starters, we work on separate steps of the plan in separate files.

Non-goals: turning this into a "proper" Python package. 

## Dependencies
- Python >= 3.5
- PyGithub: `pip install PyGithub`
- `curl`
- `git`

## Goals
Maybe use this in an action to create a "nightly build". For that we need to
provide access tokens. See
[this action documentation page](https://docs.github.com/en/actions/learn-github-actions/security-hardening-for-github-actions)
