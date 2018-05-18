grep ':ko'  data/ko00001.keg | cut -d ":" -f 2 | cut -d "]" -f 1 > data/ko_list.txt
grep "^D" data/ko00001.keg | awk '{print $2}' | sort | uniq  >  data/KO_list.txt

