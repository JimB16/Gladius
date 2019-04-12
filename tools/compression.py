# -*- coding: utf-8 -*-

import os
import sys
import zlib

# https://stackoverflow.com/questions/9050260/what-does-a-zlib-header-look-like


def compress_packet(packet, level):
    return zlib.compress(buffer(packet), level)

def decompress_packet(compressed_packet):
    return zlib.decompress(compressed_packet)

if __name__ == "__main__":
    infile = ""
    outfilename = ""
    compress = 0
    level = 1
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-x": # extract/decompress
            compress = 0
            infile = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-c": # compress
            compress = 1
            infile = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-l": # compression level
            level = int(sys.argv[i+1], 10)
            i += 2
        elif sys.argv[i] == "-o":
            outfilename = sys.argv[i+1]
            i += 2

	# optimization idea: remove bytearray and buffer usage?
    indata = open(infile, "rb").read()
	
    if compress == 0: # decompress
        output = decompress_packet(indata)
    elif compress == 1: # compress
        output = compress_packet(indata, level)
        checksum = zlib.adler32(indata)
        print "Checksum (adler32): " + hex(checksum)
	
    if not os.path.exists(os.path.dirname(outfilename)):
        os.makedirs(os.path.dirname(outfilename))
    outfile = open(outfilename, 'wb')
    outfile.write(output)
	
    '''rList = [0x78, 0x01, 0x0B, 0x08, 0x09, 0x09, 0x10, 0x60, 0x60, 0x60, 0x60, 0x06, 0x62, 0x46, 0x20, 0xF6, 0xF3, 0x0D, 0x08, 0x81, 0xF1, 0x81, 0x5C, 0x86, 0x00, 0x37, 0x0F, 0x17, 0x10, 0x1F, 0x06, 0x5C, 0xFD, 0x5C, 0xF4, 0x60, 0x7C, 0x90, 0x7A, 0x00, 0xC6, 0x21, 0x04, 0xF7]
    data = bytearray(rList)
    output = decompress_packet(buffer(data))

    out = ""
    for value in output:
        out += value.encode("hex") + ", "
        #print "test" + value.encode("hex") + "test"
    print out
	#print bytearray(output)

    packet1 = bytearray([0x1, 0x0, 0x2])
    cpacket1 = compress_packet(output, 1)
    out = ""
    for value in cpacket1:
        out += value.encode("hex") + ", "
        #print "test" + value.encode("hex") + "test"
    print "compressed: " + out'''