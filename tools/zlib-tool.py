# -*- coding: utf-8 -*-

import os
import sys
import zlib
import argparse

# https://stackoverflow.com/questions/9050260/what-does-a-zlib-header-look-like

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', action='store', nargs=2, type=str, metavar=("inputFile", "outputFile"), help="compress file")
    group.add_argument('-x', action='store', nargs=2, type=str, metavar=("inputFile", "outputFile"), help="decompress file")
    parser.add_argument("-l", type=int, default=1, help="level of compression (0-9), default=1")
    args = parser.parse_args()

    if args.x: # decompress
        # optimization idea: remove bytearray and buffer usage?
        indata = open(args.x[0], "rb").read()
        output = zlib.decompress(indata)
        outfilename = args.x[1]

    if args.c: # compress
        # optimization idea: remove bytearray and buffer usage?
        indata = open(args.c[0], "rb").read()
        output = zlib.compress(indata, args.l)
        #checksum = zlib.adler32(indata)
        #print("Checksum (adler32): " + hex(checksum))
        outfilename = args.c[1]

    if not os.path.exists(os.path.dirname(outfilename)):
        os.makedirs(os.path.dirname(outfilename))
    outfile = open(outfilename, 'wb')
    outfile.write(output)
    outfile.flush()
    outfile.close()
