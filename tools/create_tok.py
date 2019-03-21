# -*- coding: utf-8 -*-

import os
import sys
import struct


def readString(file, offset):
    file.seek(offset)
    string = ""
    char = "\0"
    while ord(char) < 128:
        char = file.read(1)
        char2 = char
        if ord(char) >= 128:
            char2 = chr(ord(char) - 128)
        string += char2
    return string

def create_tok(stringsfilepath, linesfilepath, mainfilepath, outfilepath, debug=False):
    output = ""
    string_offsets = []
    strings = []
    stringsfile = open(stringsfilepath, "rb")

    binary_data = bytearray(stringsfile.read(3))
    tuple_of_data = struct.unpack("HB", binary_data)
    string_offsets += [tuple_of_data[0] + (tuple_of_data[1] << 16)]
	
    NrOfStrings = string_offsets[0] / 3
    string_offsets = []
    stringsfile.seek(0)
    for i in range(NrOfStrings):
        binary_data = bytearray(stringsfile.read(3))
        tuple_of_data = struct.unpack("HB", binary_data)
        string_offsets += [tuple_of_data[0] + (tuple_of_data[1] << 16)]
	
	#strings
    for i in range(NrOfStrings):
        strings += [readString(stringsfile, string_offsets[i])]
        print(hex(i) + " offset: " + hex(string_offsets[i]) + " - " + strings[i])
	
	
	
    line_offsets = []
    linesfile = open(linesfilepath, "rb")
	
    binary_data = bytearray(linesfile.read(3))
    tuple_of_data = struct.unpack("HB", binary_data)
    line_offsets += [tuple_of_data[0] + (tuple_of_data[1] << 16)]
	
    NrOfLines = line_offsets[0] / 4
    line_offsets = []
    line_nrs = []
    linesfile.seek(0)
    for i in range(NrOfLines):
        binary_data = bytearray(linesfile.read(3))
        tuple_of_data = struct.unpack("HB", binary_data)
        line_offsets += [tuple_of_data[0] + (tuple_of_data[1] << 16)]
        binary_data = bytearray(linesfile.read(1))
        line_nrs += [(struct.unpack("B", binary_data))[0]]
        #print(hex(i) + " offset: " + hex(line_offsets[i]) + " - " + str(line_nrs[i]))
	
    lines = []
    for i in range(NrOfLines):
        sentence = ""
        linesfile.seek(line_offsets[i])
        for j in range(line_nrs[i]):
            binary_data = bytearray(linesfile.read(1))
            Byte = (struct.unpack("B", binary_data))[0]
            if Byte >= 128:
                binary_data = bytearray(linesfile.read(1))
                Byte2 = (struct.unpack("B", binary_data))[0]
                Byte += (Byte2 - 1) * 0x80
                #if Byte2 == 0x15:
                #    Byte += 0xa00
                #elif Byte2 == 0x2:
                #    Byte += 0x80
            sentence += strings[Byte] + " "
        lines += [sentence]
	
        #print hex(i) + ": " + sentence
	

    i = 0
    outfile = open(outfilepath, 'wb')
    mainfile = open(mainfilepath, "rb")
    filesize = os.path.getsize(mainfilepath)
    while i < filesize:
        pos = mainfile.tell()
        #binary_data = bytearray([i%100])
        binary_data = bytearray(mainfile.read(1))
        Byte = (struct.unpack("B", binary_data))[0]
        i += 1
        if Byte >= 128:
            binary_data = bytearray(mainfile.read(1))
            Byte2 = (struct.unpack("B", binary_data))[0]
            i += 1
            Byte += ((Byte2-1) * 0x80)
        #print hex(pos) + ": " + lines[Byte]
        #outfile.write(hex(Byte) + ": " + lines[Byte] + "\n")
        outfile.write(lines[Byte].strip() + "\n")

    return output


if __name__ == "__main__":
    filename = ''
    mainfile = ''
    stringsfilepath = ""
    linesfilepath = ""
    outfile = ""
    debugFlag = False
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-strings":
            stringsfilepath = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-lines":
            linesfilepath = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-main":
            mainfile = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-o":
            outfile = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-debug":
            filelist_on = 0
            debugFlag = True
            i += 2
        else:
            i += 1

    output = create_tok(stringsfilepath, linesfilepath, mainfile, outfile, debugFlag)
    print output
