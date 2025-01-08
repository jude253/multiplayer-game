load("@aspect_bazel_lib//lib:run_binary.bzl", "run_binary")
load("@rules_python//python:py_binary.bzl", "py_binary")
load("@rules_python//python:py_library.bzl", "py_library")
load("@rules_python//python/entry_points:py_console_script_binary.bzl", "py_console_script_binary")

py_library(
    name = "lib",
    srcs = glob(["**/*.py"]),
    visibility = ["//visibility:public"],
    deps = [
        "@multiplayer-game//game_assets",
        "@multiplayer-game//lib",
        "@pypi//fastapi",
        "@pypi//pygame",
        "@pypi//websockets",
    ],
)

py_binary(
    name = "main",
    srcs = glob(["**/*.py"]),
    data = [],
    deps = [
        "@multiplayer-game//game_assets",
        "@multiplayer-game//lib",
        "@pypi//fastapi",
        "@pypi//pydantic",
        "@pypi//websockets",
    ],
)

# To run: bazel run //server:fastapi_dev_v1
py_console_script_binary(
    name = "fastapi_dev_v1",
    args = [
        "dev",
        "server/v1/app.py",
    ],
    pkg = "@pypi//fastapi",
    script = "fastapi",
    visibility = ["//visibility:public"],
    deps = [
        "@multiplayer-game//game_assets",
        "@multiplayer-game//lib",
        "@multiplayer-game//server:lib",
        "@pypi//pydantic",
        "@pypi//websockets",
    ],
)

# To run: bazel run //server:fastapi_prod_v1
py_console_script_binary(
    name = "fastapi_prod_v1",
    args = [
        "run",
        "server/v1/app.py",
    ],
    pkg = "@pypi//fastapi",
    script = "fastapi",
    visibility = ["//visibility:public"],
    deps = [
        "@multiplayer-game//game_assets",
        "@multiplayer-game//lib",
        "@multiplayer-game//server:lib",
        "@pypi//pydantic",
        "@pypi//websockets",
    ],
)

# similar to pyinstaller server/main.py --workpath pygame-out/client/build --distpath pygame-out/client/dist --specpath pygame-out/client --name client.command --onefile --clean
# To run command: bazel build //server:release
run_binary(
    name = "release",
    srcs = ["//server:lib"],
    args = [
        "server/main.py",
        "--workpath",
        "$(RULEDIR)/pygame-out/build",
        "--distpath",
        "$(RULEDIR)/pygame-out/dist",
        "--specpath",
        "$(RULEDIR)/pygame-out",
        "--collect-data",
        "game_assets",
        "--clean",
        "--name",
        "server",
        "--onefile",
    ],
    env = {
        # Needed to ensure that bazel has permissions to write to cache dir!
        # See: https://pyinstaller.org/en/stable/usage.html#supporting-multiple-operating-systems
        "PYINSTALLER_CONFIG_DIR": "$(RULEDIR)/pygame-out/cache",
    },
    out_dirs = ["pygame-out"],
    tool = "//:pyinstaller",
)
