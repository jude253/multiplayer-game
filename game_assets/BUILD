load("@rules_python//python:py_library.bzl", "py_library")

py_library(
    name = "game_assets",
    srcs = glob(["**/*.py"]),
    data = glob([
        # MAKE SURE TO ADD RELEVANT FILE EXTENSIONS HERE!!
        "**/*.txt",
        "**/*.gif",
    ]),
    visibility = ["//:__subpackages__"],
    deps = [],
)
