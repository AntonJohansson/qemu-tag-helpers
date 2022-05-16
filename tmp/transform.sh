#!/bin/sh

in=$1
out=$2

#cp $in $out
clang $in -S -emit-llvm -o ${in}.ll
clang ${in}.ll -c -o ${out}
