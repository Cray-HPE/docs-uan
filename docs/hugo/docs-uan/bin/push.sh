#!/usr/bin/env bash

set -ex
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$THIS_DIR/.."
pwd
[[ -d docs-uan ]] && rm -rf docs-uan || echo "docs-uan doesn't exist"
mkdir -p docs-uan
cd docs-uan
pwd
git clone --depth=1 -b release/docs-html https://github.com/Cray-HPE/docs-uan.git docs-uan
ls -laR
rm -rf docs-uan/* docs-uan/.gitignore
ls -laR
cp -r $THIS_DIR/../public/* docs-uan
cd docs-uan
ls -la
git config --global user.name 'git@github.com'
git add .
git commit --amend --no-edit
git push --force origin release/docs-html
