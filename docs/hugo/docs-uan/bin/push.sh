#!/usr/bin/env bash

set -ex
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$THIS_DIR/.."
pwd
[[ -d docs-uan ]] && rm -rf docs-uan || echo "docs-uan doesn't exist"
mkdir -p docs-uan
cd docs-uan
pwd
git config --global user.name github-actions
git config --global user.email noreply@hpe.com
git clone --depth=1 -b release/docs-html https://github.com/Cray-HPE/docs-uan.git docs-uan
rm -rf docs-uan/* docs-uan/.gitignore
cp -r $THIS_DIR/../public/* docs-uan
cd docs-uan
git add .
git commit --amend --no-edit
git push --force origin release/docs-html
