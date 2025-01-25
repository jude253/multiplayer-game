# Overview

This creates infrastructure for AWS using CDK.

# Initial run command
```
bazel run -- @pnpm//:pnpm --dir <full/path/to/package/root> run cdk list
```

# Install `node_modules` in src for development and intellisense

```
bazel run -- @pnpm//:pnpm --dir $PWD install
```