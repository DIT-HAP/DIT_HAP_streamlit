#!/bin/bash

for file in $(find ../data/resource/pombe_gocam -name "*.yaml"); do
    gocam convert --dot-layout -I yaml -O cx2 $file -o ../data/resource/pombe_gocam_cx2/$(basename $file .yaml).cx2
done