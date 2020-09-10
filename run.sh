#!/bin/bash

if [ "$#" -gt 1 ]; then
  echo "Usage: ./run.sh"
  exit 1
fi

while true
do
  echo "Warning! Duplicate filenames will be overwritten"
  echo "Are you sure to continue? [Y/N]"
  read input

  if [ ${input,,} == "y" ]; then
    break
  elif [ ${input,,} == "n" ]; then
    exit 1
  else
    continue
  fi
done

echo "==============================="

if [ "$#" -eq 1 ]; then
  if [ ! -f "$1" ]; then
    echo "File $1 does not exist!"
    exit 1
  fi
  if [[ ! ("$1" == *".jpg"*) ]]; then
    echo "File must have jpg format!"
    exit 1
  fi

  aws s3 cp "$1" s3://sdcc-images

  echo "Job done! File is in S3 bucket!"
  exit 0
fi

if [ ! -d "./images" ]; then
  echo "Images directory does not exist! Please keep the directory in the correct place."
  exit 1
fi

#upload images on S3 bucket in order to execute the training phase
for file in ./images/*.jpg
do
  #loer case trasformation
  file=${file,,}
  #if new item has an existing correspondent S3 object, it will overwrite the existing one with the new one
  aws s3 cp "$file" s3://sdcc-images
done

echo "================================="
echo "Job done! Files are in S3 bucket!"
echo "================================="
echo "Starting browser"
firefox index.html
exit 0
