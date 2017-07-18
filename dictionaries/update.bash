#!/bin/bash

declare -a arr=("french_custom" "english_custom" "plain_words" "hashtags")

input="$HOME/Code/BeatCrunch/dictionaries"
output="$HOME/nltk_data/corpora/stopwords"

for a in "${arr[@]}" ; do
  echo "Updating $a"
  uniq ${input}/${a} | sort > ${output}/${a}
  wc -l ${output}/${a}
  cp ${output}/${a} ${input}/${a}
done
