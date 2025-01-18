filegroup(
    name = "cpp_files",
    srcs = glob(["**/*.cpp"]),
)

filegroup(
    name = "header_files",
    srcs = glob(["**/*.h"]),
)

# Might need to change the embed file to only have one file or folder
filegroup(
    name = "includes",
    srcs = glob(["include/**/*.ttf"]),
)

# bazel build //wasm_client:main
genrule(
    name = "main",
    srcs = [
        ":cpp_files",
        ":header_files",
        ":includes",
    ],
    outs = [
        "index.html",
        "index.js",
        "index.wasm",
    ],
    cmd = "$(execpaths @//:emcc) **/src/**/*.cpp --use-port=sdl2 --use-port=sdl2_ttf --embed-file=$(location :includes)@/include/fonts/SourceCodePro-Regular.ttf -o $(RULEDIR)/index.html",
    executable = False,
    tools = ["@//:emcc"],
    visibility = ["//visibility:public"],
)
