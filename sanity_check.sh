#! /bin/bash

cat KPI/node_layer2.csv | awk -F, 'BEGIN{OFS=","}{print $1,$7,$9}' | sort -n -k 3 -t ',' | less -S
