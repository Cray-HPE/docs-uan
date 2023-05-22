#!/usr/bin/env bash

rm -rf build/docs/
mkdir build
mkdir build/docs

dita -i uan_combined.ditamap -o build/docs/ -f markdown_github &&\
mv build/docs/index.md build/docs/SUMMARY.md &&\
cp index.md build/docs/index.md &&\
cp mkdocs.yml build/mkdocs.yml