# create tmp subdir
mkdir tmp
# copy all markdown files to the tmp subdir
cp ./*/*.md tmp/
# copy both ditamaps to the tmp subdir 
cp ./*.ditamap tmp/
# convert links in the UAN IG ditamap
sed -i 's/installation_prereqs\///' tmp/uan_install_guide.ditamap
sed -i 's/install\///' tmp/uan_install_guide.ditamap
sed -i 's/operations\///' tmp/uan_install_guide.ditamap
sed -i 's/advanced\///' tmp/uan_install_guide.ditamap

# convert links in the UAN AG ditamap
sed -i 's/advanced\///' tmp/uan_admin_guide.ditamap
sed -i 's/operations\///' tmp/uan_admin_guide.ditamap
sed -i 's/troubleshooting\///' tmp/uan_admin_guide.ditamap

# convert all links in all Markdown files. 
# for every file in "ls tmp/*.md", for every string in "installation_prereqs, install, operations, advanced, troubleshooting", replace that string with nothing
declare -a prefixes=("\.\.\/installation_prereqs" "\.\.\/install" "\.\.\/operations" "\.\.\/advanced" "\.\.\/troubleshooting")
for file in $(ls tmp/*.md);do for prefix in ${prefixes[@]}; do sed -i "s/$prefix\///g" $file;done;done
