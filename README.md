# DOCS-UAN

## Overview

The docs-uan repository holds the documentation and documentation publication tooling
for the HPE Cray EX User Access Nodes (UAN) product. Documentation in HTML format is generated from the Markdown source files
using:

- the [Hugo](https://gohugo.io/) static site generation framework for the combined documentation available at https://cray-hpe.github.io/docs-uan.
- The [DITA Open Toolkit](https://www.dita-ot.org/) (DITA-OT) for the official HPE Cray UAN [Installation](https://support.hpe.com/connect/s/search?language=en_US#q=s-8032) and [Administration](https://support.hpe.com/connect/s/search?language=en_US#q=s-8033) Guides that are published to the HPE Support Center (HPESC) portal.

## Documentation Source

The UAN documentation source is located under the `docs/portal/developer-portal` directory
of this repository.  All documentation must be in Markdown format. The table of contents
for the combined UAN documentation, including each topic/chapter subdirectories, is generated from the
`hugo_toc.json` file which defines the order of the topics/chapters in the generated HTML.

When new topics/chapters are created, or if the title/heading is changed in existing
documentation, the `hugo_toc.json` file must be updated to reflect the changes.  The following
section describes the `hugo_toc.json` file format.

The official HPE Cray UAN guides are maintained as DITA 1.3 ditamaps which include the same Markdown source files as the Hugo-generated combined docs. We update the ditamap files and `hugo_toc.json` files simultaneously.

### hugo_toc.json

The order of elements in this file, along with the `weight` values for each topic, define
the order of the generated table of contents (`_index.md`) file for each topic.

Here's an example of the `hugo_toc.json` file with annotations:

```json
[
  { ### DO NOT EDIT THIS SECTION ###
    "title": "UAN Documentation",
    "dir": "/",
    "weight": 10
  },
  { ### DO NOT EDIT THIS SECTION ###
    "title": "Cray Ex User Access Nodes Installation And Administration Guide",
    "dir": "/",
    "weight": 15
  },
  { ### This section defines the order of the index for the `installation_prereqs` directory ###
    "title": "Installation Prereqs",  ### Title in the generated index file ###
    "dir": "installation_prereqs",  ### directory in the docs/portal/developer-portal tree ###
    "weight": 20, ### Order in the index.  Lower value to high. ###
    "toc": [ ### List of pages, in order, of this chapter/topic ###
        "Prepare_for_UAN_Product_Installation.md",
        "Configure_the_BMC_for_UANs_with_iLO.md",
        "Configure_the_BIOS_of_an_HPE_UAN.md",
        "Configure_the_BIOS_of_a_Gigabyte_UAN.md"
    ]
  },
  { ### This is used to order pages within a chapter/topic. ###
    "title": "Prepare For UAN Product Installation", ### Title (must match the heading in the source file) ###
    "weight": 1 ### Order within the chapter ###
  },
  {
    "title": "Configure The BMC For UANs With iLO",
    "weight": 2
  },
  {
    "title": "Configure The BIOS Of An HPE UAN",
    "weight": 23
  },
  {
    "title": "Configure The BIOS Of A Gigabyte UAN",
    "weight": 24
  },
  { 
    "title": "Install",
    "dir": "install",
    "weight": 30,
    "toc": [
        "Install_the_UAN_Product_Stream.md"
    ]
  },
  .... Additional chapter/topics ....
]
```

## Generating the Combined HTML Documentation

Generating the combined HTML documentation is performed by the *make* command with the *Makefile.hugo* file. There are three options to allow flexibility in building and publishing the documentation.

* `make -f Makefile.hugo` builds the documentation to the `docs/hugo/docs-uan/public` directory.
  * `make -f Makefile.hugo build_hugo_docs` is equivalent to the above command.
* `make -f Makefile.hugo publish_hugo_docs` publishes a previously built set of the documentation to the UAN GitHub Pages location. (https://cray-hpe.github.io/docs-uan)
* `make -f Makefile.hugo build_and_publish_hugo_docs` builds and publishes the documentation to the UAN GitHub Pages location. (https://cray-hpe.github.io/docs-uan)

## How We Generate the Official HPE Cray UAN Documentation

For each public release, an information developer runs the `build.sh` script which:
  1. builds the HTML5 output for both guides using a local DITA-OT installation 
  1. bundles the HTML5 output of each guide with an HPESC-required metadata JSON file.
  1. zips the HTML5 and metadata files for each guide into its own archive for uploading, reviewing, and publishing.

## Benefits of This Hybrid Markdown and DITA Approach

- Ease of Markdown authoring for software developers
- Ability to use Markdown tooling for authoring content
- We can use all the map-level DITA content reuse and conditionalization features
- The ditamaps support the map-level metadata required by our custom DITA-OT plugin
- We can publish from the same source files using both the Hugo SSG and DITA-OT
- The ditamaps can include topic files written in other formats supported by DITA-OT ("full" DITA, rST, etc.)
- Since the content is already in Markdown, this eases possible adoption of the MDITA authoring format of the proposed
Lightweight DITA (LwDITA) standard in the future
