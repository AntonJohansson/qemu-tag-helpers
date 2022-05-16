#!/bin/sh

clang TagHelpersPass.cpp -shared -o pass -lLLVM-13 -fPIC -g
clang main.c -S -emit-llvm
opt -enable-new-pm=0 -load ./pass main.ll --TagHelpersPass -S -o main.new.ll
#clang main.new.ll
