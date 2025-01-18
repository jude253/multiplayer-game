filegroup(
    name = "cpp_files",
    srcs = glob(["**/*.cpp"]),
)

filegroup(
    name = "header_files",
    srcs = glob(["**/*.h"]),
)

# bazel build //wasm_client:main
genrule(
    name = "main",
    srcs = [
        ":cpp_files",
        ":header_files",
    ],
    outs = [
        "index.html",
        "index.js",
        "index.wasm",
    ],
    cmd = "$(execpaths @//:emcc) **/*.cpp --use-port=sdl2 -o $(RULEDIR)/index.html",
    executable = False,
    tools = ["@//:emcc"],
    visibility = ["//visibility:public"],
)
