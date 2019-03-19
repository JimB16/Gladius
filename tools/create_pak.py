# -*- coding: utf-8 -*-

import os
import sys
import struct


def create_pak(dir, filename, becmap, debug=False):
    output = ""
    NrOfFiles = 0x0
	
    filepaths = []
    filesizes = []
    fileoffsets = []
    filenameoffsets = []
    FileMagic = []
    with open(becmap) as fin:
        for line in fin:
            words = line.split() # filename, ?, offset, flags?, filesize
            if len(words) == 5:
                filepath = dir + "/" + words[0]
                filepaths += [filepath]
                FileSize = os.path.getsize(filepath)
                filesizes += [FileSize]
                FileMagic += [int(words[3], 16)]
                filenameoffsets += [int(words[4], 16)]
                fileoffsets += [int(words[1], 16)]
            elif len(words) == 1:
                NrOfFiles = int(words[0], 16)
    
    # update file offsets with new file sizes
    addr = fileoffsets[0]
    for i in range(NrOfFiles):
        if i < (NrOfFiles-1):
            addr += filesizes[i] + (4-1)
            addr &= (0x100000000-4)
            fileoffsets[i+1] = addr
        
    if os.path.dirname(filename) != "":
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
    output_rom = open(filename, 'wb')
	
    # write header
    output_rom.write(struct.pack('<4s', "PAK1"))
    output_rom.write(struct.pack('<I', int(NrOfFiles)))
    
    for i in range(NrOfFiles):
        output_rom.write(struct.pack('<I', int(filenameoffsets[i])))
        output_rom.write(struct.pack('<I', int(fileoffsets[i])))
        output_rom.write(struct.pack('<I', int(filesizes[i])))
        output_rom.write(struct.pack('<I', int(FileMagic[i])))
    
	# write filename strings
    for i in range(NrOfFiles):
        output_rom.write(os.path.basename(filepaths[i]))
        output_rom.write(struct.pack('<B', int(0)))
    
    while((output_rom.tell() % 0x4) != 0):
        output_rom.write(struct.pack('<B', int(0xaf)))

	# write file data into package
    for i in range(NrOfFiles):
        filepart = bytearray(open(filepaths[i], "rb").read())
        output_rom.write(filepart)
        while((output_rom.tell() % 0x4) != 0):
            output_rom.write(struct.pack('<B', int(0xaf)))
    
    return output


if __name__ == "__main__":
    filename = ''
    becmap = ''
    dir = ''
    debugFlag = False
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-dir":
            dir = sys.argv[i+1]
            i += 2
        if sys.argv[i] == "-becmap":
            becmap = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-o":
            filename = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-debug":
            filelist_on = 0
            debugFlag = True
            i += 2
        else:
            i += 1

    output = create_pak(dir, filename, becmap, debugFlag)
    print output
