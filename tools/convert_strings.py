# -*- coding: utf-8 -*-

import os
import sys
import struct
import operator


def compressTok(filename, inputfile, debug=False):
    list_file = []
    strings = []
    output = ""
    strings += [""]
    filesize = 0
	
    with open(inputfile) as fin:
        i = 1
        for line in fin:
            #if line.strip() == "":
            #    continue
            #newline = ""
            words = line.split()
            if words[0] == "//":
                continue
			
            '''words = line.split("^Either^Either^")
            if len(words) != 2:
                print(line)'''
            words = line.split("^")
            if len(words) >= 4:
                while str(i) != words[0]:
                    strings += [""]
                    filesize += 1
                    i += 1
                string = words[3].rstrip("\r\n").replace("\\r\\n", "\n")
                strings += [string]
                filesize += len(string)+1
                i += 1
            else:
                print(line)
        
    if os.path.dirname(filename) != "":
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
    output_rom = open(filename, 'wb')
	# write strings in file
    offset = (len(strings))*4+2*4
    filesize += offset + 1
    output_rom.write(struct.pack('<I', int(len(strings))))
    output_rom.write(struct.pack('<I', int(filesize)))
    for string in strings:
        output_rom.write(struct.pack('<I', int(offset)))
        offset += len(string) + 1
    for string in strings:
        output_rom.write(struct.pack('<' + str(len(string)+1) + 's', string + '\0'))
	
    return output


if __name__ == "__main__":
    filename = ''
    inputfile = ''
    debugFlag = False
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-i":
            inputfile = sys.argv[i+1]
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

    output = compressTok(filename, inputfile)
	
    print output
