import json
import os
import sys
import xml.etree.ElementTree as ET


#source_dir = sys.argv[1]
source_dir = "../../../portal/developer-portal/"


def gen_dir_toc(doc_dir):
    toc_list = []
    with os.scandir(doc_dir) as md_dir:
        for entry in md_dir:
            if entry.is_file() and entry.name.split(".")[-1] == "md":
                toc_list.append(entry.name)
    return(toc_list)


def extract_title(md_file):
    md_fo = open(md_file, "r", encoding="utf-8")
    hdr_string = md_fo.readline()
    #print(md_file)
    md_first_line = hdr_string.split("# ")[1]
    md_title = md_first_line.split("\n")[0]
    md_fo.close()
    return(md_title)


output_json = []
ig_include = []
top_titles_fp = open(source_dir + "top_titles.json", "r")
top_titles = json.load(top_titles_fp)
for title in top_titles:
    if "title" in title:
        output_json.append(title)
    if "ig_include" in title:
        ig_include.append(title["ig_include"])
top_titles_fp.close()
weight = 10
with open(source_dir + "uan_install_guide.ditamap", 'r+', encoding="utf-8") as install_map:
    tree = ET.parse(install_map)
    install_map_root = tree.getroot()
    for child in install_map_root:
        if child.tag == "topicref":
            topic_ref_path = child.get("href")
            topic_title = extract_title(source_dir + topic_ref_path)
            if ig_include.count(topic_title) == 1:
                weight = weight + 10
                output_json.append({"title": topic_title, "weight": weight})
                topic_weight = 0
                for grandchild in child.findall("./topicref"):
                    topic_weight = topic_weight + 1
                    topic_ref_path = grandchild.get("href")
                    topic_title = extract_title(source_dir + topic_ref_path)
                    output_json.append({"title": topic_title, "weight": weight + topic_weight})
        if child.tag == "topichead" or child.tag == "topicset":
            group_navtitle = child.find("./topicmeta/navtitle")
            group_title = group_navtitle.text
            if ig_include.count(topic_title) == 1:
                weight = weight + 10
                output_json.append({"title": group_title, "weight": weight})
                topic_weight = 0
                for grandchild in child.findall("./topicref"):
                    topic_weight = topic_weight + 1
                    topic_ref_path = grandchild.get("href")
                    topic_title = extract_title(source_dir + topic_ref_path)
                    output_json.append({"title": topic_title, "weight": weight + topic_weight})
with open(source_dir + "uan_admin_guide.ditamap", 'r+', encoding="utf-8") as admin_map:
    tree = ET.parse(admin_map)
    admin_map_root = tree.getroot()
    for child in admin_map_root:
        if child.tag == "topicref":
            topic_ref_path = child.get("href")
            topic_title = extract_title(source_dir + topic_ref_path)
            weight = weight + 10
            output_json.append({"title": topic_title, "weight": weight})
            topic_weight = 0
            for grandchild in child.findall("./topicref"):
                topic_weight = topic_weight + 1
                topic_ref_path = grandchild.get("href")
                topic_title = extract_title(source_dir + topic_ref_path)
                output_json.append({"title": topic_title, "weight": weight + topic_weight})
        if child.tag == "topichead" or child.tag == "topicset":
            group_navtitle = child.find("./topicmeta/navtitle")
            group_title = group_navtitle.text
            weight = weight + 10
            output_json.append({"title": group_title, "weight": weight})
            topic_weight = 0
            for grandchild in child.findall("./topicref"):
                topic_weight = topic_weight + 1
                topic_ref_path = grandchild.get("href")
                topic_title = extract_title(source_dir + topic_ref_path)
                output_json.append({"title": topic_title, "weight": weight + topic_weight})
output_json_string = json.dumps(output_json, indent=2, separators=(',', ':'))
print(output_json_string)
##    output_json_file = open(source_dir + "/hugo_toc.json", "w")
##    output_json_file.write(output_json_string)
##    output_json_file.close()


    


def old_main():
   with os.scandir(source_dir) as dir_item:
        output_json = []
        top_titles_fp = open(source_dir + "/top_titles.json", "r")
        top_titles = json.load(top_titles_fp)
        for title in top_titles:
            output_json.append(title)
        top_titles_fp.close()
        for entry in dir_item:
            hugo_json_path = os.path.join(entry, "hugo_toc.json")
            if entry.is_dir() and os.path.exists(hugo_json_path):
                toc_fp = open(hugo_json_path)
                toc = json.load(toc_fp)
                toc_block = gen_dir_toc(entry)
                toc["toc"] = toc_block
                output_json.append(toc)
                weight = toc["weight"]
                for file in os.scandir(entry):
                    if file.is_file() and file.name.split(".")[-1] == "md":
                        weight = weight + 1
                        full_md_path = os.path.join(entry, file.name)
                        md_title = extract_title(full_md_path)
                        output_json.append({"title": md_title, "weight": weight})
                toc_fp.close()
        output_json_string = json.dumps(output_json, indent=2, separators=(',', ':'))
        output_json_file = open(source_dir + "/hugo_toc.json", "w")
        output_json_file.write(output_json_string)
        output_json_file.close()
