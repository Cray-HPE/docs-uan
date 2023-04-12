import json
import os
import sys


source_dir = sys.argv[1]


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
    md_first_line = hdr_string.split("# ")[1]
    md_title = md_first_line.split("\n")[0]
    md_fo.close()
    return(md_title)


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
    #print(output_json_string)
    output_json_file = open(source_dir + "/hugo_toc.json", "w")
    output_json_file.write(output_json_string)
    output_json_file.close()
