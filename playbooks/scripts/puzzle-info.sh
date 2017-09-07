#!/usr/bin/env bash
# puzzle-info.sh [PUZZLE_INFO_CSV] -- find available puzzles and info about them
PUZZLE_INFO_CSV=$1

find ~/fetch/ -maxdepth 1 -type d -name solution\* | sort | awk -F '_' 'BEGIN {OFS=","; print "dir", "id"}{print $0, $2}' > tmp1.csv

find ~/fetch/ -maxdepth 1 -type d -name "solution_*" -exec stat {} --printf="{},%y\n" \; | sort | awk 'BEGIN { OFS=","; print "dir", "last_modified" } { print $0 }' | join -t "," --header tmp1.csv - > tmp2.csv

find ~/fetch/ -maxdepth 1 -name "solution_*" -type d -exec find {}/top -maxdepth 1 -name "*.pdb" -print -quit \; 2> /dev/null | awk -F '/top/' '{ print $1 }' | sort | awk 'BEGIN {OFS=","; print "dir", "top"} { print $0, 1 }' | join -t "," --header -a 1 tmp2.csv - > tmp3.csv

find ~/fetch/ -maxdepth 1 -name "solution_*" -type d -exec find {}/all -maxdepth 2 -name "*.pdb" -print -quit \; 2> /dev/null | awk -F '/all/' '{ print $1 }' | sort | awk 'BEGIN {OFS=","; print "dir", "all"} { print $0, 1 }' | join -t "," --header -a 1 tmp3.csv - > ${PUZZLE_INFO_CSV}

rm tmp*.csv
