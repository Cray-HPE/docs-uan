import json
import os
import sys
import xml.etree.ElementTree as ET


source_dir = sys.argv[1]
#source_dir = "../../../portal/developer-portal/"
weight = 10

# generates the "toc" structure for top-level ditamap elements that have child elements
# title_file_path is for handling when ditamaps use a Markdown file to nest others
def gen_dir_toc(subtree, title_file_path=None):
    toc_list = []
    if title_file_path != None:
        toc_list.append(title_file_path)
    for grandchild in child.findall("./topicref"):
        toc_list.append(grandchild.get("href"))
    return(toc_list)

# extracts the level-1 heading from a Markdown file
# This function will error if a Level 1 heading is not in the very first line of the file
def extract_title(md_file):
    md_fo = open(md_file, "r", encoding="utf-8")
    hdr_string = md_fo.readline()
    md_first_line = hdr_string.split("# ")[1]
    md_title = md_first_line.split("\n")[0]
    md_fo.close()
    return(md_title)


def parse_ditamap(map_file, ig=False):
    with open(map_file, 'r+', encoding="utf-8") as ditamap:
        tree = ET.parse(ditamap)
        ditamap_root = tree.getroot()
        global child # made this a global to pass in as "subtree" to gen_dir_toc
        for child in ditamap_root:
            if child.tag == "topicref":
                topic_ref_path = child.get("href")
                topic_title = extract_title(source_dir + topic_ref_path)
                if ig_include.count(topic_title) == 1 or ig == False: 
                    global weight # required because we don't want the top-level count reset every time we enter this function
                    weight = weight + 10 # counter for top-level Markdown files and headings
                    topic_weight = 0 # counter for child Markdown files
                    # if this element has children, build out the "toc" to include them
                    # the "toc" must be within the same JSON element as the parent.
                    if len(child.findall("./topicref")) > 0:
                        output_json.append({"title": topic_title, "weight": weight, "toc": gen_dir_toc(child, topic_ref_path)})
                        topic_weight = topic_weight + 1
                        #  . . . include the parent Markdown file itself
                        output_json.append({"title": topic_title, "weight": weight + topic_weight})
                    else:
                        output_json.append({"title": topic_title, "weight": weight})
                    # this loop creates separate title/weight entries for the children
                    for grandchild in child.findall("./topicref"):
                        topic_weight = topic_weight + 1
                        topic_ref_path = grandchild.get("href")
                        topic_title = extract_title(source_dir + topic_ref_path)
                        output_json.append({"title": topic_title, "weight": weight + topic_weight})
            # currently we only use topicheads, just future-proofing. Unlikely we'll use DITA <topicgroups>
            # Much of the above processing is re-implemented here, except that here we're dealing with just ditamap headings
            if child.tag == "topichead" or child.tag == "topicset":
                # the ditamaps must follow the recent DITA spec that recommends the <navititle> element, not attr
                # for this code to work
                group_navtitle = child.find("./topicmeta/navtitle")
                group_title = group_navtitle.text
                if ig_include.count(topic_title) == 1 or ig == False:
                    weight = weight + 10
                    if len(child.findall("./topicref")) > 0:
                        output_json.append({"title": group_title, "weight": weight, "toc": gen_dir_toc(child)})
                    else:
                        output_json.append({"title": group_title, "weight": weight})
                    topic_weight = 0
                    for grandchild in child.findall("./topicref"):
                        topic_weight = topic_weight + 1
                        topic_ref_path = grandchild.get("href")
                        topic_title = extract_title(source_dir + topic_ref_path)
                        output_json.append({"title": topic_title, "weight": weight + topic_weight})
    
output_json = []
ig_include = []
# the ig_include items are level 1 titles of unique Install Guide files we want
# to include in the merged JSON. This is needed because many files
# are in both guides, but organized differently
top_titles_fp = open(source_dir + "top_titles.json", "r")
top_titles = json.load(top_titles_fp)
for item in top_titles:
    if "title" in item:
        output_json.append(item)
    if "ig_include" in item:
        ig_include.append(item["ig_include"])
top_titles_fp.close()
parse_ditamap(source_dir + "uan_install_guide.ditamap", ig=True)
parse_ditamap(source_dir + "uan_admin_guide.ditamap", ig=False)
output_json_string = json.dumps(output_json, indent=2, separators=(',', ':'))
# write to file
print(output_json_string)

