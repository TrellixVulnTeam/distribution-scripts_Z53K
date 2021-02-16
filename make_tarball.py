#!/usr/bin/env python3
#
# This script is intended to implement step 4 of
# <https://hackmd.io/AWds-AnZT72XXsbA0oVC6A>, i.e.:
#
# 4. Create archives: run a script which takes a git ref (a sha1, a tag such  "v4.11.3") as argument. 

print("TODO: parse arguments")

#     - fetches the code from the given git ref in the GAP repository

print("TODO: invoke `git archive`")

#     - fetches the versioned packages tarball

print("TODO: download package distro tarballs")
# TODO: also use existing tarballs if present, so that during retry on
# does not have to download again?
# TODO: add checksum validation?

#     - extracts packages in the code from git

print("TODO: extract package archive, either via Python package or by invoking `tar`")

#     - build the GAP manual via `make doc`

print("TODO: run `make doc`")

#     - (possibly regenerates packages manuals as well???)
#     - remove LaTeX build artifacts

print("TODO: remove unwanted files")


#     - run `tar`  to create `.tar.gz` (and perhaps also `.tar.xz`)

print("TODO: create tarballs from all")


