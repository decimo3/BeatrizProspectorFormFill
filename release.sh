#!/bin/env bash

set -e

if [[ -z "$VIRTUAL_ENV" ]]; then
	python -m venv .venv
    source .venv/Scripts/activate
fi

git fetch --tags # Fetch git tags and get the latest one
version=$(git describe --tags $(git rev-list --tags --max-count=1))
version_number="${version#v}"  # Remove 'v' prefix if the tag has it

# Extract major, minor, and patch versions
IFS='.' read -r MAJOR_VERSION MINOR_VERSION PATCH_VERSION <<< "$version_number"
export MAJOR_VERSION MINOR_VERSION PATCH_VERSION

# Write version file
envsubst < version.txt > version_file.tmp
mv version_file.tmp version.txt
cat version.txt

# Install dependencies
pip install -r requirements.txt

# Build executable with pyinstaller
pyinstaller -n lnc_bot --clean --icon appicon.ico --version-file version.txt --paths src src/lnc_bot.py

# Restore files with sensible data
cp src/lnc_bot.ini src/lnc_bot.ini.bak
git restore src/lnc_bot.ini

# Compress executable and related files
rm lnc_bot.zip
cd dist/lnc_bot ; zip -r ../../lnc_bot.zip ./* ; cd ../..
cd src ; zip -r ../lnc_bot.zip lnc_bot.ini path.ini Resources/*.lang ; cd ..

# Create a release on GitHub
gh release create $version --verify-tag --notes-file release.md --title "lnc_bot ${version} release" lnc_bot.zip

# Reverting placeholder files
git restore version.txt
