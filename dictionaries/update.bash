#!/bin/bash

declare -a arr=("french_custom" "english_custom" "plain_words")

input="/Users/greg/Code/BeatCrunch/dictionaries"
output="/Users/greg/nltk_data/corpora/stopwords"

for a in "${arr[@]}" ; do
  echo "Updating $a"
  uniq ${input}/${a} | sort > ${output}/${a}
  wc -l ${output}/${a}
  cp ${output}/${a} ${input}/${a}
done
