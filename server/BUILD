load("@aspect_bazel_lib//lib:run_binary.bzl", "run_binary")
load("@rules_python//python:py_binary.bzl", "py_binary")
load("@rules_python//python:py_library.bzl", "py_library")

py_library(
    name = "lib",
    srcs = glob(["**/*.py"]),
    visibility = ["//visibility:public"],
    deps = [
        "@multiplayer-game//game_assets",
        "@multiplayer-game//lib",
        "@pypi//pygame",
    ],
)

py_binary(
    name = "main",
    srcs = glob(["**/*.py"]),
    data = [],
    deps = [
        "@multiplayer-game//game_assets",
        "@multiplayer-game//lib",
        "@pypi//pygame",
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
