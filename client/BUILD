load("@aspect_bazel_lib//lib:run_binary.bzl", "run_binary")
load("@rules_python//python:py_binary.bzl", "py_binary")
load("@rules_python//python:py_library.bzl", "py_library")

py_library(
    name = "lib",
    srcs = glob(["**/*.py"]),
    visibility = ["//:__subpackages__"],
    deps = [
        "@multiplayer-game//game_assets",
        "@multiplayer-game//lib",
        "@pypi//pygame",
        "@pypi//requests",
        "@pypi//websockets",
        "@pypi//websocket_client",  # Import name for websocket-client

        # Explicitly referencing this as Bazel does not seem to pick
        # this up as being a depenency of "@multiplayer-game//lib".
        # Maybe I should use a wheel file or something for the lib
        # to ensure the dependencies are captured correctly.
        "@pypi//pydantic",
    ],
)

py_binary(
    name = "main",
    srcs = glob(["**/*.py"]),
    data = [],
    deps = [
        "@multiplayer-game//game_assets",
        "@multiplayer-game//lib",
        "@pypi//pydantic",  # See note above
        "@pypi//pygame",
        "@pypi//requests",
        "@pypi//websocket_client",  # Import name for websocket-client
        "@pypi//websockets",
    ],
)

py_binary(
    name = "v1_client",
    srcs = ["@multiplayer-game//client:lib"],
    data = [],
    main = "client/v1/client.py",
    deps = [
        "@multiplayer-game//game_assets",
        "@pypi//pydantic",  # See note above
        "@pypi//pygame",
        "@pypi//requests",
        "@pypi//websocket_client",  # Import name for websocket-client
        "@pypi//websockets",
    ],
)

py_binary(
    name = "v2_client",
    srcs = ["@multiplayer-game//client:lib"],
    data = [],
    main = "client/v2/client.py",
    deps = [
        "@multiplayer-game//game_assets",
        "@pypi//pydantic",  # See note above
        "@pypi//pygame",
        "@pypi//requests",
        "@pypi//websocket_client",  # Import name for websocket-client
        "@pypi//websockets",
    ],
)

# similar to pyinstaller client/main.py --workpath pygame-out/client/build --distpath pygame-out/client/dist --specpath pygame-out/client --name client.command --onefile --clean
# To run command: bazel build //client:release
run_binary(
    name = "release",
    srcs = ["//client:lib"],
    args = [
        "client/main.py",
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
        "client",
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
