#!/usr/bin/env python
import os
import sys
import subprocess
import shutil

if len(sys.argv) < 2:
    print("No target specified!")
    print("USAGE:")
    print("  localize <binary> [relative_path]")
    sys.exit(0)

target = sys.argv[1]
out_path = "lib"
if len(sys.argv) == 3:
    out_path = sys.argv[2]

def import_paths_and_relink(binary, paths=None):
    lines = subprocess.check_output("otool -l {} | grep path".format(binary), shell=True)
    rpaths = [x.strip()[5:].split(" (offset")[0] for x in lines.split("\n") if "path " in x]
    if paths is None:
        paths = rpaths
    names = [x.strip()[5:].split(" (offset")[0] for x in lines.split("\n") if "name " in x]
    copied = 0
    existed = 0

    if out_path != "." and not os.path.exists(out_path):
        os.makedirs(out_path)

    # step 1: collect all files
    for name in names:
        if name.startswith("@rpath/"):
            for p in paths:
                combined = "{}/{}".format(p, name[7:])
                if os.path.exists(combined):
                    # copy into place
                    target_path = "{}/{}".format(out_path, name[7:])
                    if os.path.exists(target_path):
                        existed += 1
                        break
                    shutil.copyfile(combined, target_path)
                    copied += 1
                    copied += import_paths_and_relink(target_path, paths)
                    break
        elif name.startswith("@loader_path/"):
            pass

    if copied == 0 and existed == 0:
        print("No dependencies found for {}!".format(binary))

    # step 2: remove rpath directives
    for p in rpaths:
        os.system("install_name_tool -delete_rpath \"{}\" \"{}\"".format(p, binary))

    if rpaths:
        # step 3: add the new rpath directive
        os.system("install_name_tool -add_rpath \"@executable_path/{}\" \"{}\"".format(out_path, binary))
    return copied + existed

copied = import_paths_and_relink(target)

print("{} rpath directives relinked, {} dependencies imported.".format(target, copied))
