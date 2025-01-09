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

exports_files(
    ["requirements_lock.txt"],
    visibility = ["//visibility:public"],
)
