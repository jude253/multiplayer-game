load("@rules_python//python:py_library.bzl", "py_library")
load("@rules_python//python:py_test.bzl", "py_test")

# This is only for linting.  Might be better to use a filegroup or something
py_library(
    name = "test_lib",
    srcs = glob(["**/*.py"]),
    visibility = ["//:__subpackages__"],
)

py_test(
    name = "lib_default_test",
    srcs = glob(["lib/**/*.py"]),
    main = "lib/test.py",
    deps = ["//lib"],
)
