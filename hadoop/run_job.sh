#!/bin/bash

INPUT=$1
OUTPUT=$2
D=$3
X=$4
Y=$5

hdfs dfs -rm -r -f "$OUTPUT"

hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -file mapper.py \
  -file reducer.py \
  -mapper "python3 mapper.py $D $X $Y" \
  -reducer "python3 reducer.py" \
  -input "$INPUT" \
  -output "$OUTPUT"
