import os
from pathlib import Path

if __name__ == "__main__":
    """
    This script creates a `.env` file at the workspace root that will
    set the PYTHONPATH environment variable to the bazel environment
    variable of BUILD_WORKSPACE_DIRECTORY.  This allows the virtual
    environment to find the local bazel python modules by adding the
    root directory of these modules to the .env file. 

    See:
    - https://bazel.build/docs/user-manual#running-executables

    This script should work on all platforms.
    """
    build_workspace_dirctory = Path(os.environ["BUILD_WORKSPACE_DIRECTORY"])
    env_filename = ".env"
    set_pythonpath_env_var_str = f'PYTHONPATH="{build_workspace_dirctory}"'
    print(f"Making .env file with {set_pythonpath_env_var_str}")
    with open(os.path.join(build_workspace_dirctory, env_filename), "w+") as f:
        f.writelines([set_pythonpath_env_var_str])
    print(f"Successfully created .env file with {set_pythonpath_env_var_str}!")
