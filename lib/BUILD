load("@rules_python//python:packaging.bzl", "py_package", "py_wheel")
load("@rules_python//python:py_library.bzl", "py_library")
load("@rules_python//python:py_test.bzl", "py_test")

py_library(
    name = "lib",
    srcs = glob(["**/*.py"]),
    visibility = ["//:__subpackages__"],
    deps = [
        "@multiplayer-game//game_assets",
        "@pypi//pydantic",
        "@pypi//pygame",
    ],
)

py_test(
    name = "lib_default_test",
    srcs = [
        "@multiplayer-game//test:test_lib",
    ],
    main = "lib/test.py",
    deps = ["//lib"],
)

py_test(
    name = "test_dummy_game",
    srcs = [
        "@multiplayer-game//test:test_lib",
    ],
    main = "lib/test_dummy_game.py",
    deps = ["//lib"],
)

# Maybe this can help to import dependencies automaticatlly or something:
# https://rules-python.readthedocs.io/en/latest/api/rules_python/python/packaging.html#PyWheelInfo
# Taken from here: https://github.com/bazelbuild/rules_python/blob/main/examples/wheel/BUILD.bazel
# NOTE: Stuck on some error: //lib:whl' does not have mandatory providers: 'PyInfo' or 'CcInfo'
py_package(
    name = "pkg",
    # Only include these Python packages.
    packages = ["lib"],
    visibility = ["//:__subpackages__"],
    deps = [":lib"],
)

py_wheel(
    name = "whl",
    # Package data. We're building "lib_package_whl-0.0.1-py3-none-any.whl"
    distribution = "lib_package_whl",
    python_tag = "py3",
    version = "0.0.1",
    visibility = ["//:__subpackages__"],
    deps = [":pkg"],
)
