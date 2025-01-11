load("@rules_python//python:py_library.bzl", "py_library")

py_library(
    name = "test_lib",
    srcs = glob(["**/*.py"]),
    visibility = ["//:__subpackages__"],
)

py_test(
    name = "test_client_server",
    srcs = [
        "@multiplayer-game//test:test_lib",
    ],
    main = "general/test_client_server.py",
    deps = [
        "@multiplayer-game//client:lib",
        "@multiplayer-game//game_assets",
        "@multiplayer-game//lib",
        "@multiplayer-game//server:lib",
    ],
)
