#!/usr/bin/env bash

set -ex
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
[[ -d docs-uan ]] && rm -rf docs-uan || echo "docs-uan doesn't exist"
mkdir -p docs-uan
git clone --no-checkout --depth=1 -b release/docs-html https://github.com/Cray-HPE/docs-uan.git docs-uan
rm -rf docs-uan/docs-uan/* docs-uan/docs-uan/.gitignore
cp -r $THIS_DIR/../public/* docs-uan/docs-uan/
cd docs-uan/docs-uan
git add .
git commit --amend --no-edit
git push --force origin release/docs-html
