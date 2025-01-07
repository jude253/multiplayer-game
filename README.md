# Overview
This repo contains code for a multiplayer game, both a server and client
and a python libarary for both the server and client and a game assets
library that can be included on the client and/or server and in the 
debug bazel script as well as in the PyInstaller release

## Details
This is a monorepo that uses bazel as the build system and PyInstaller
to make a game using pygame.  Debug/development bazel binaries are
created for the server/client using `py_binary` as this is quicker to
build for development changes.  Release builds are created using
PyInstaller because it is able to build binaries/applications for all
operating systems with all dependencies included.  There is a number of
configuration options availble for PyInstaller, and this has not been
finalized yet.  Ideally, this release build will be able to make a
clickable application for windows/mac/pc eventually.  However, intially
it makes a binary that can be run from the terminal.  This can maybe
be renamed and given additional permissions to run by clicking on
certain operating systems.


### Doc links
- https://bazel.build/
- https://www.pygame.org/news
- https://pyinstaller.org/en/stable/index.html
- https://github.com/bazelbuild/rules_python

# Dependency Management
Bazel is used for the build system and the `pip.bzl` extension is used
for pulling down pythin packages.  The python package dependencies and
versions for the entire project are all in the `requirements.in` and
a requirements lockfile is generated using `pip_compile` in a command
that is specified in the top level `BUILD` file.  This lockfile then
makes all the specified packages available to use as a bazel dependency
by starting the prefix `@pypi//`.  For example, `@pypi//pygame` is one
dependency insalled from `pip.bzl`. The individual dependencies for 
python packages/binaries/libraries created in this project are specified
using the bazel `deps = [...]` specification, as this will only pull in
the needed packages to the target, not all python pacakges specified in
the project level `requirements.in`.  Additionally, python packages
created in this project are pulled in by using the prefix
`@multiplayer-game//`.  For example, `@multiplayer-game//lib` is a
python package dependency created in this project.

The release binary of the server/client is created using PyInstaller
due to its ability to make binaries bundled with the dependences/data
for multiple platforms.  However, since Bazel is used for the build
system and may package python packages/data differently that what
PyInstaller is built for, the `game_assets` python pacakge doesn't use
the [Bazel Python libraries](https://github.com/bazelbuild/rules_python/tree/main/python/runfiles)
[runfiles](https://bazel.build/rules/lib/builtins/runfiles) for handling
data for fear that PyInstaller will not be able to bundle the runfiles
constructs into the release binary.  Instead, this same sort of approach
is used but using the built-in Python library `importlib.resources`.
This data can then be bundled into the release binaries by using the
`--collect-data` option for PyInstaller.