load("@npm//:defs.bzl", "npm_link_all_packages")
load("@rules_python//python:py_binary.bzl", "py_binary")
load("@rules_python//python/entry_points:py_console_script_binary.bzl", "py_console_script_binary")
load("@rules_uv//uv:pip.bzl", "pip_compile")
load("@rules_uv//uv:venv.bzl", "create_venv")

py_console_script_binary(
    name = "pyinstaller",
    pkg = "@pypi//pyinstaller",
    visibility = ["//visibility:public"],
    deps = [
        # This needs to have the dependencies needed by pyinstaller available
        # in order for the dependencies to be included!
        "@multiplayer-game//game_assets",
        "@multiplayer-game//lib",
        "@pypi//pygame",
        "@pypi//pydantic",
        "@pypi//requests",

        # Not sure if this is needed, may put server in exe, may not.
        # fastapi-cli may also be needed too.
        "@pypi//fastapi",
    ],
)

# To run: bazel run //:black
# Similar to (with .venv running): black client/**/*.py game_assets/**/*.py lib/**/*.py server/**/*.py
py_console_script_binary(
    name = "black",
    args = [
        # In order to use the $(rootpaths) "make variable", the libs to
        # be linted are needed to be listed as dependencies.
        "$(rootpaths @multiplayer-game//game_assets)",
        "$(rootpaths @multiplayer-game//lib)",
        "$(rootpaths @multiplayer-game//client:lib)",
        "$(rootpaths @multiplayer-game//server:lib)",
        "$(rootpaths @multiplayer-game//test:test_lib)",
        "-v",
    ],
    data = [
        "@multiplayer-game//:.gitignore",
        "@multiplayer-game//:pyproject.toml",
    ],
    pkg = "@pypi//black",
    visibility = ["//visibility:public"],
    deps = [
        # Include packages to be linted as dependencies, then they can
        # be referenced in the args.  Black will follow symlinks to
        # update the sources or maybe the executable gets the `rootpath`
        # from the $(rootpaths) "make variable".
        "@multiplayer-game//game_assets",
        "@multiplayer-game//lib",
        "@multiplayer-game//client:lib",
        "@multiplayer-game//server:lib",
        "@multiplayer-game//test:test_lib",
    ],
)

py_console_script_binary(
    name = "fastapi",
    pkg = "@pypi//fastapi",
    visibility = ["//visibility:public"],
    deps = [
        "@multiplayer-game//game_assets",
        "@multiplayer-game//lib",
        "@multiplayer-game//server:lib",
    ],
)

# To run: bazel run @@//:generate_requirements_lock_txt
pip_compile(
    name = "generate_requirements_lock_txt",
    requirements_in = "//:requirements.in",
    requirements_txt = "//:requirements_lock.txt",
)

# This is for intellisense and includes all packages.
# To run: bazel run @@//:create_venv
# To remove: rm -rf .venv
create_venv(
    name = "create_venv",
    destination_folder = ".venv",
    requirements_txt = "//:requirements_lock.txt",
)

# Run this to set the environment variable PYTHONPATH in .env file to
# allow virtual environment to find local python modules.
# To run: bazel run @@//:create_env_file
py_binary(
    name = "create_env_file",
    srcs = ["//:tools/create_env_file.py"],
)

exports_files(
    ["requirements_lock.txt"],
    visibility = ["//visibility:public"],
)

################################################################################
# EMSCRIPTEN
################################################################################
# This is pretty janky at the moment, but it's the first way I was able
# to get emscipten/emsdk/emcc to run.  I'd like to have it integrate
# naturally with Bazel, but I can't wrap my head around why it isn't
# working following the bazel tutorial on the bazel website or in the
# /bazel dirctory in emsdk.

# bazel build //:install_emsdk
genrule(
    name = "install_emsdk",
    srcs = [
        "@emsdk//:emsdk_files",
        "@emsdk//:emsdk_bin",
    ],
    outs = [
        "activate_latest_log.txt",
    ],
    cmd = "./$(locations @emsdk//:emsdk_bin) install latest && ./$(locations @emsdk//:emsdk_bin) activate latest > $@",
)

# Make wrapper around emcc that sets correct env vars allows passing in args
# bazel run //:emcc

# Issue installing libharfbuzz on MacOS solved by using newer version of python
# for emscripten python:
# https://github.com/bazelbuild/rules_python/discussions/1926
# https://github.com/emscripten-core/emscripten/issues/20986
# https://rules-python.readthedocs.io/en/latest/toolchains.html#toolchain-usage-in-other-rules
genrule(
    name = "emcc",
    srcs = [
        "@emsdk//:emsdk_bin",
        "@emsdk//:emsdk_files",
    ],
    outs = [
        "emcc.sh",
    ],
    # activate latest emscritpen, run script that sets environment vars, then export this to an .sh file for execution that takes input args
    cmd = "BAZEL_PYTHON_PATH=$$(readlink -f $(PYTHON3)) && ACTIVATE_STR=$$(./$(locations @emsdk//:emsdk_bin) activate latest | sed '14q;d') && echo \"export EMSDK_QUIET=1 && $$ACTIVATE_STR && export EMSDK_PYTHON=$$BAZEL_PYTHON_PATH && emcc \\$$@\" > $@",
    executable = True,
    toolchains = ["@rules_python//python:current_py_toolchain"],
    tools = ["@//:install_emsdk"],
    visibility = ["//visibility:public"],
)

# https://github.com/aspect-build/rules_js/blob/main/docs/pnpm.md#rules-overview
npm_link_all_packages(
    name = "node_modules",
)
