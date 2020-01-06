# -*- coding: utf-8 -*-

import os
import sys
import struct
import argparse
import hashlib
import gladiushashes


# UNPACK PAK
#############

def WriteSectionInFile(file, dirname, filename, addr, size):
    if not os.path.exists(os.path.dirname(dirname + filename)):
        os.makedirs(os.path.dirname(dirname + filename))
        
    file.seek(addr)
    fByteArray = bytearray(file.read(size))
    m = hashlib.md5()
    m.update(fByteArray)
	
    md5 = m.hexdigest()
    if md5 in gladiushashes.hashes:
        filename2 = dirname + gladiushashes.hashes[md5]
        outfilename = gladiushashes.hashes[md5]
    else:
        filename2 = dirname + filename
        outfilename = filename
	
    if not os.path.exists(os.path.dirname(filename2)):
        os.makedirs(os.path.dirname(filename2))
    f = open(filename2, 'wb')
    f.write(fByteArray)
        
    print("Write out file " + filename2 + " " + m.hexdigest())
	
    return outfilename

def ReadString0(file, address, size):
    file.seek(address)
    string = ""
    bytes = bytearray(file.read(size))
    for i in range(size):
        if(bytes[i] != 0):
            string += chr(bytes[i])
        else:
            break
    return string


def unpack_pak(filename, filedir, outFileList, debug=False):
    file = open(filename, "rb+")
    header_output = pak_diagnose(file, filedir, debug)

    headerfilename = filedir + outFileList
    if not os.path.exists(os.path.dirname(headerfilename)) and os.path.dirname(headerfilename):
        os.makedirs(os.path.dirname(headerfilename))
    fheader = open(headerfilename, 'w')
    fheader.write(header_output)


def pak_diagnose(file, filedir="", debug=False):
    output = ""

    file.seek(0x4)
    data = file.read(2)
    NrOfFiles, = struct.unpack("<H", data)
    print("Nr of Files: " + hex(NrOfFiles))
    output += hex(NrOfFiles) + "\n"

    DataOffset = []
    DataSize = []
    DataMagic = []
    DataStringOffset = []
    for i in range(NrOfFiles):
        file.seek(0x8+0x10*i)
        data = file.read(0x10)
        DataStringOffset_, DataOffset_, DataSize_, DataMagic_ = struct.unpack("<IIII", data)
        DataStringOffset += [DataStringOffset_]
        DataOffset += [DataOffset_]
        DataSize += [DataSize_]
        DataMagic += [DataMagic_]

    filename = ""
    for i in range(NrOfFiles): # NrOfFiles
        filename = ReadString0(file, DataStringOffset[i], 0x20)
        filename2 = WriteSectionInFile(file, filedir, filename, DataOffset[i], DataSize[i])
        print(filename2)
        output += filename2 + " " + hex(DataOffset[i]) + " " + hex(DataSize[i]) + " " + hex(DataMagic[i]) + " " + hex(DataStringOffset[i]) + "\n"

    return output



# PACK PAK
###########


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
    output_rom.write(struct.pack('<4s', b"PAK1"))
    output_rom.write(struct.pack('<I', int(NrOfFiles)))
    
    for i in range(NrOfFiles):
        output_rom.write(struct.pack('<I', int(filenameoffsets[i])))
        output_rom.write(struct.pack('<I', int(fileoffsets[i])))
        output_rom.write(struct.pack('<I', int(filesizes[i])))
        output_rom.write(struct.pack('<I', int(FileMagic[i])))
    
	# write filename strings
    for i in range(NrOfFiles):
        output_rom.write((os.path.basename(filepaths[i])).encode('utf-8'))
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
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-pack', action='store', nargs=3, type=str, metavar=("inputDir", "Filelist", "outputFile"), help="pack pak-file")
    group.add_argument('-x', action='store', nargs=3, type=str, metavar=("inputFile", "outFolder", "Filelist"), help="extract pak-file")
    args = parser.parse_args()

    debug = True

    if args.pack:
        output = create_pak(args.pack[0], args.pack[2], args.pack[1], debug)
        print(output)
    if args.x:
        unpack_pak(args.x[0], args.x[1], args.x[2])
