#!/usr/bin/env python3

import argparse
import json
import os
import shlex
import sys
import subprocess
import re

def find_compile_commands(clang_path, input_path):
    if os.path.exists("compile_commands.json"):
        with open("compile_commands.json", "r") as compile_commands_file:
            compile_commands = json.load(compile_commands_file)
            for compile_command in compile_commands:
                path = compile_command["file"]
                if path != input_path:
                    continue

                os.chdir(compile_command["directory"])
                command = compile_command["command"]
                argv = shlex.split(command)
                argv[0] = clang_path
                return argv

    # If we coulnd't find "compile_commands" just default
    # to the following.
    return [clang_path, input_path]

def generate_llvm_ir(clang_path, input_path, output_path):
    argv = find_compile_commands(clang_path, input_path)
    for i, arg in reversed(list(enumerate(argv))):
        if arg in {'-MQ', '-o', '-MF'}:
            del argv[i:i+2]

    argv += ["-S", "-emit-llvm", "-o", output_path]

    print(" ".join(argv))

    proc = subprocess.Popen(argv)
    if proc.wait() != 0:
        print("Command: %s exited with %d\n" % (" ".join(argv), proc.returncode))

def link(llvm_link_path, ll_paths, output_path):
    command = [llvm_link_path, "-S"] + ll_paths + ['-o', output_path]
    proc = subprocess.Popen(command)
    if proc.wait() != 0:
        print("Command: %s exited with %d\n" % (" ".join(command), proc.returncode))

def temp_file(file):
    filename, _ = os.path.splitext(os.path.basename(file))
    new_file = os.path.join(os.path.dirname(file), filename)
    new_file += ".ll"
    return new_file

def main():
    parser = argparse.ArgumentParser(description='Produce the LLVM IR for a given source file.')
    parser.add_argument("clang",       metavar="CLANG_PATH",            help="Path to clang.")
    parser.add_argument("llvm_link",   metavar="LLVM_LINK_PATH",        help="Path to llvm-link")
    parser.add_argument("opt",         metavar="OPT_PATH",              help="Path to opt")
    parser.add_argument('passes',      metavar='LLVM_PASSES',           help='Path to library containing LLVM passes')
    parser.add_argument('output',      metavar='OUTPUT_PATH',           help='Path to output file')
    parser.add_argument('input_paths', metavar='INPUT_PATH', nargs='+', help='Source file input path')
    args = parser.parse_args()


    # Generate LLVM IR
    ll_paths = []
    for input_path in args.input_paths:
        if input_path.endswith(".inc"):
            continue
        print(input_path)
        output_path = temp_file(input_path)
        ll_paths.append(output_path)
        generate_llvm_ir(args.clang, input_path, output_path)
    print(ll_paths)

    # Todo might be worth to have pre-pass that goes over module
    # and checks if it contains any attribute we care about.
    # We could then reject the entire module if not.
    #
    # Profile this!

    # link together llvm-ir
    ll_out = temp_file("input")
    link(args.llvm_link, ll_paths, ll_out)

    step1_out = temp_file("step1")
    command = [
        args.opt,
        '-enable-new-pm=0',
        '-load',
        args.passes,
        ll_out,
        '--TagHelpersPass',
        '-S',
        '-o',
        step1_out
    ]

    print(" ".join(command))

    proc = subprocess.Popen(command)
    if proc.wait() != 0:
        print("Command: %s exited with %d\n" % (" ".join(command), proc.returncode))

    proc = subprocess.Popen([args.clang, '-c', step1_out, '-o', args.output])
    if proc.wait() != 0:
        print("#lol")

if __name__ == "__main__":
    sys.exit(main())
