#!/bin/bash

# Expects the following environment variables to be set:
#   $NEW_VERSION                 (Example: "1.2.0")
#   $NEW_VERSION_PYTHON          (Example: "1.2.0a0")

# This will fail the Maven build if the version is not available.
# Thankfully, this is not the case (yet) in this project.
# If/when it happens, this needs to be replaced by a manually provided version,
# as scanning the text of the POM would be unreliable.
echo "     New version: $NEW_VERSION"
echo "     New Python Version: $NEW_VERSION_PYTHON"
mvn versions:update-parent "-DparentVersion=[$NEW_VERSION,$NEW_VERSION]" -DallowSnapshots=true -DgenerateBackupPoms=false
mvn versions:update-child-modules
sed -i "s/^timefold_solver_python_version.*=.*/timefold_solver_python_version = '$NEW_VERSION_PYTHON'/" setup.py
git commit -am "build: switch to version $NEW_VERSION_PYTHON"