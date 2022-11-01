# gpl2aco.py
# Original script by mieki256
# https://gist.github.com/mieki256/b230c5dc678ed3363f15b7ed7a38c935

#!python
# -*- mode: python; Encoding: utf-8; coding: utf-8 -*-
# Last updated: <2021/07/08 04:18:55 +0900>
"""
Convert GIMP palette (.gpl) to Photoshop color swatch (.aco).
usage: python gpl2aco.py GPL_FILE ACO_FILE
Windows10 x64 20H2 + Python 3.9.5 64bit
"""
import sys
import re
import struct
import argparse

def load_and_parse_gpl(lines):
    name = ""
    columns = 0
    colors = []

    pat1 = re.compile(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(.+)$')
    pat2 = re.compile(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s*$')

    # with open(filepath) as f:
    #     lines = f.read()

    linenum = 0
    for l in lines.split("\n"):
        linenum += 1
        if linenum == 1:
            if l.find("GIMP Palette") == 0:
                print("Found [GIMP Plaette]")
                continue
            else:
                return None, None, None
                #print("Error: This file is not a GIMP palette.")
                #sys.exit()

        if len(l) == 0 or l[0] == '#':
            continue

        if l.find("Name:") == 0:
            name = l[5:].strip()
            print("Found Name: [%s]" % name)
        elif l.find("Columns:") == 0:
            columns = int(l[8:].strip())
            print("Found Columns: [%d]" % columns)
        else:
            # r g b colorname
            r = pat1.match(l)
            if r:
                r, g, b, cname = r.groups()
                colors.append([int(r), int(g), int(b), cname])
            else:
                r = pat2.match(l)
                if r:
                    r, g, b = r.groups()
                    colors.append([int(r), int(g), int(b), ""])
                else:
                    print("Error: Syntax [%s] in line %d" % (l, linenum))
                    sys.exit()

    return name, columns, colors


def create_aco(vernum, nonull, colors):
    aco_ver = vernum  # 1 or 2
    col_len = len(colors)
    bindata = struct.pack(">2H", aco_ver, col_len)

    cspace = 0  # color ID 0 = RGB
    for c in colors:
        r, g, b, color_name = c

        w = int(65535 * r / 255)
        x = int(65535 * g / 255)
        y = int(65535 * b / 255)
        z = 0

        bindata += struct.pack(">5H", cspace, w, x, y, z)

        if vernum == 2:
            if nonull == False:
                name_len = len(color_name) + 1
                bindata += struct.pack(">L", name_len)
                for s in list(color_name):
                    n = ord(s)
                    bindata += struct.pack(">H", n)

                # add NULL word
                bindata += struct.pack(">H", 0)
            else:
                name_len = len(color_name)
                bindata += struct.pack(">L", name_len)
                for s in list(color_name):
                    n = ord(s)
                    bindata += struct.pack(">H", n)

    return bindata


def main():
    # parse argv
    desc = "Convert GIMP palette (.gpl) to Photoshop color swatch (.aco)"
    p = argparse.ArgumentParser(description=desc)
    p.add_argument("gpl_file", help="Input GIMP palette file (.gpl)")
    p.add_argument("aco_file", help="Output Photoshop swatch file (.aco)")
    p.add_argument("--nonull", help="Exclude null from color name",
                   action='store_true', default=False)
    args = p.parse_args()

    infile = args.gpl_file
    outfile = args.aco_file
    print("input file: %s" % infile)
    print("output file: %s" % outfile)
    nonull = args.nonull

    # load and parse gpl file
    name, columns, colors = load_and_parse_gpl(infile)

    # for c in colors:
    #     print(c)

    print("Found Color length: %d" % len(colors))

    # create aco binary ver1 and ver2
    aco_bin = create_aco(1, nonull, colors)
    aco_bin += create_aco(2, nonull, colors)

    # write aco file
    print("Write: %s" % outfile)
    with open(outfile, 'wb') as f:
        f.write(aco_bin)


if __name__ == '__main__':
    main()