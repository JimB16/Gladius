# -*- coding: utf-8 -*-

import os
import sys
import struct
import operator
import argparse


# UNCOMPRESS SKILLS.TOK
########################

def readString(file, offset):
    file.seek(offset)
    string = ""
    char = "\0"
    while ord(char) < 128:
        char = chr(ord(file.read(1)))
        char2 = char
        if ord(char) >= 128:
            char2 = chr(ord(char) - 128)
        string += char2
    return string

def create_tok(stringsfilepath, linesfilepath, mainfilepath, outfilepath, debug=False):
    string_offsets = []
    strings = []
    stringsfile = open(stringsfilepath, "rb")

    binary_data = bytearray(stringsfile.read(3))
    tuple_of_data = struct.unpack("HB", binary_data)
    string_offsets += [tuple_of_data[0] + (tuple_of_data[1] << 16)]
	
    NrOfStrings = int(string_offsets[0] / 3)
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
	
    NrOfLines = int(line_offsets[0] / 4)
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
            sentence += strings[Byte] + " "
        lines += [sentence]


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
        outfile.write((lines[Byte].strip() + "\n").encode('utf-8'))


# COMPRESS SKILLS.TOK
######################


def compressTok(filename, filename2, filename3, inputfile, debug=False):
    dic_strings = {} # dictionary with string and nr of appearances
    dic_lines = {} # dictionary with lines and nr of appearances
    list_file = []
	
    with open(inputfile) as fin:
        for line in fin:
            if line.strip() == "":
                continue
            newline = ""
            words = line.split()
            for word in words:
                word = word.strip().rstrip(",")
                if word == "//": # skip rest of line after a comment
                    continue
                if (word in dic_strings):
                    dic_strings[word] += 1
                else:
                    dic_strings[word] = 1
                newline += word + " "
            if newline in dic_lines:
                dic_lines[newline] += 1
            else:
                dic_lines[newline] = 1
            list_file += [newline]


    if debug:
        if os.path.dirname("./stringsdebug.txt") != "":
            if not os.path.exists(os.path.dirname("./stringsdebug.txt")):
                os.makedirs(os.path.dirname("./stringsdebug.txt"))
        stringsdebug = open("./stringsdebug.txt", 'wb')
        absoffset = 0
        nrofStrings = 0
        sorted_strings = sorted(dic_strings.items(), key=operator.itemgetter(1), reverse=True)
        for key, val in sorted_strings:
            dic_strings[key] = nrofStrings
            #print key, "=>", val
            string_ = key + " => " + hex(dic_strings[key]) + "\n"
            stringsdebug.write(string_.encode('utf-8'))
            absoffset += len(key)
            nrofStrings += 1
        #print("nrofStrings*3: " + hex(nrofStrings*3))
        #print("absoffset: " + hex(absoffset))


    if os.path.dirname(filename) != "":
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
    output_rom = open(filename, 'wb')
	# write strings in file
    offset = nrofStrings*3
    for key, val in sorted_strings:
        output_rom.write(struct.pack('<H', int(offset)))
        offset += len(key)
        output_rom.write(struct.pack('<B', int(0)))
    for key, val in sorted_strings:
        string = key[:-1]
        string += chr(ord(key[len(key)-1]) + 0x80)
        output_rom.write(string.encode('utf-8'))



    if os.path.dirname("./linedebug.txt") != "":
        if not os.path.exists(os.path.dirname("./linedebug.txt")):
            os.makedirs(os.path.dirname("./linedebug.txt"))
    linedebug = open("./linedebug.txt", 'wb')
    absoffset = 0
    nrofLines = 0
    linesInByts = []
    sorted_lines = sorted(dic_lines.items(), key=operator.itemgetter(1), reverse=True)
    for key, val in sorted_lines:
        dic_lines[key] = nrofLines
        #print key, "=>", nrofLines
        string = key + " => " + hex(dic_lines[key]) + "\n"
        linedebug.write(string.encode('utf-8'))
        lineInBytes = []
        words = key.split()
        for word in words:
            byte1 = dic_strings[word] % 0x80
            if dic_strings[word] >= 0x80:
                byte1 += 0x80
                lineInBytes += [byte1]
                byte2 = ((dic_strings[word]) / 0x80)
                lineInBytes += [byte2]
            else:
                lineInBytes += [byte1]
        absoffset += len(lineInBytes)
        nrofLines += 1
        linesInByts += [lineInBytes]
    #print("nrofLines*4: " + hex(nrofLines*4))
    #print("absoffset: " + hex(absoffset))
        
    if os.path.dirname(filename2) != "":
        if not os.path.exists(os.path.dirname(filename2)):
            os.makedirs(os.path.dirname(filename2))
    output_rom2 = open(filename2, 'wb')
	# write strings in file
    offset = nrofLines*4
    i = 0
    for key, val in sorted_lines:
        output_rom2.write(struct.pack('<H', int(offset)))
        words = key.split()
        line = linesInByts[i]
        offset += len(line)
        output_rom2.write(struct.pack('<B', int(0)))
        output_rom2.write(struct.pack('<B', int(len(words))))
        i += 1
    for bytelist in linesInByts:
        for byte in bytelist:
            output_rom2.write(bytes(int(byte)))


    if os.path.dirname(filename3) != "":
        if not os.path.exists(os.path.dirname(filename3)):
            os.makedirs(os.path.dirname(filename3))
    output_rom3 = open(filename3, 'wb')
	# write line nrs in file
    i = 0
    data = []
    byte1 = 0
    byte2 = 0
    for line in list_file:
        byte2 = 0
        testvalue = dic_lines[line]
        byte1 = testvalue % 0x80
        if testvalue >= 128:
            byte1 += 0x80
            data += [byte1]
            byte2 = (testvalue / 0x80)
            data += [byte2]
        else:
            data += [byte1]
        i += 1
        #print dic_lines[line], line, byte1, byte2
	
    for byte in data:
        output_rom3.write(bytearray(int(byte)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', action='store', nargs=4, type=str, metavar=("inputFile", "outputFile1", "outputFile2", "outputFile3"), help="compress skills.tok file")
    group.add_argument('-x', action='store', nargs=4, type=str, metavar=("inputFile1", "inputFile2", "inputFile3", "outputFile"), help="decompress skills.tok file")
    args = parser.parse_args()

    debug = True

    if args.c:
        compressTok(args.c[1], args.c[2], args.c[3], args.c[0], debug)
    if args.x:
        create_tok(args.x[0], args.x[1], args.x[2], args.x[3], debug)
