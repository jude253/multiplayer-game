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
    ],
)

# To run: bazel run //:black
py_console_script_binary(
    name = "black",
    args = [
        # In order to use the $(rootpaths) "make variable", the libs to
        # be linted are needed to be listed as dependencies.
        "$(rootpaths @multiplayer-game//game_assets)",
        "$(rootpaths @multiplayer-game//lib)",
        "$(rootpaths @multiplayer-game//client:lib)",
        "$(rootpaths @multiplayer-game//server:lib)",
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
    ],
)

py_console_script_binary(
    name = "fastapi",
    pkg = "@pypi//fastapi",
    visibility = ["//visibility:public"],
    deps = [
        # This needs to have the dependencies needed by pyinstaller available
        # in order for the dependencies to be included!
        "@multiplayer-game//game_assets",
        "@multiplayer-game//server:lib",
        "@multiplayer-game//lib",
        "@pypi//pygame",
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
