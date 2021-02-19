#!/usr/bin/env python3

# TODO: do the following, for manual use (or perhaps in a GitHub Action?)
#
#  # 1. switch to right branch
#  `git checkout stable-4.11`   # or maybe assume this was done and 

#  2. now edit configure.ac to set version, release date & year
#
#  3. now run `make` to update derived files containing the version which are also in the repo.
#     TODO: change this: instead of letting the build system do these transformations,
#     perhaps this scripts should do them? I think then also create_stable_branch needs to do it.
#     The relevant files are currently CITATION,  doc/versiondata
#
#  4. commit and push:
#      git commit -m "Version 4.X.Y" -a  # commit it all
#      git tag -m "Version 4.X.Y" v4.X.Y  # annotated tag, could also be signed in the future
#      git push

error("TODO")
