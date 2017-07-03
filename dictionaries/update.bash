#!/bin/bash

declare -a arr=("french_custom" "english_custom" "plain_words")

input="~/Code/BeatCrunch/dictionaries/"
output="~/nltk_data/corpora/stopwords/"

for a in "${arr[@]}" ; do
  echo "Updating $a"
  uniq ${input}${a} | sort > ${output}${a}
  wc -l ${output}${a}
  cp ${output}${a} ${input}${a}
done
