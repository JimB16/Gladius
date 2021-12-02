# -*- coding: utf-8 -*-

import os
import sys
import struct
import operator
import argparse
import time
import hashlib
import gladiushashes
import queue
import threading
from collections import namedtuple
import zlib


separator = ','


class RomSection():
    def __init__(self, name, compname, hash, address, compsize, flags, size, checksum, checksum2):
        self.name = name
        self.compname = compname
        self.hash = hash
        self.address = address
        self.new_address = address
        self.flags = flags
        self.size = size
        self.compsize = compsize
        self.checksum = checksum
        self.checksum2 = checksum2


# UNPACK BEC-ARCHIVE
#####################


def ReadSection(file, addr, size):
    file.seek(addr)
    return file.read(size)

def WriteSectionInFile(fByteArray, dirname, filename, size, debug=False):
    filename2 = dirname + filename
    if not os.path.exists(os.path.dirname(filename2)):
        os.makedirs(os.path.dirname(filename2))
    outFile = open(filename2, 'wb')
    outFile.write(fByteArray)
    outFile.flush()
    outFile.close()

    print("Write out file " + filename2)

def GetFilenameOfFile(file, addr, size, pathhash, i, debug=False):
    if pathhash in gladiushashes.pathhashes:
        return gladiushashes.pathhashes[pathhash]

    file.seek(addr)
    fByteArray = file.read(size)
    m = hashlib.md5()
    m.update(fByteArray)
    md5 = m.hexdigest()
    if md5 in gladiushashes.hashes:
        return gladiushashes.hashes[md5]

    return GetNumberedFilenameOfFile(file, addr, i)

def GetNumberedFilenameOfFile(file, Offset, i):
    filename = ""
    if ReadHWord(file, Offset) == 0x2f2f:
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x0D0A2F2F):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x0D0A0D0A) and (ReadHWord(file, Offset+4) == 0x2F2F):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x436F7079) and (ReadWord(file, Offset+4) == 0x72696768):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x56455253):
        filename = str(i) + ".vers"
    elif (ReadWord(file, Offset) == 0x50545450):
        filename = str(i) + ".pttp"
    elif (ReadWord(file, Offset) == 0x50414B31):
        filename = str(i) + ".pak1"
    elif (ReadWord(file, Offset) == 0x23233832) and (ReadWord(file, Offset+4) == 0x32300D0A):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x1D200000):
        filename = str(i) + ".bin"
    elif (ReadWord(file, Offset) == 0x504D5332):
        filename = str(i) + ".pms2"
    elif (ReadWord(file, Offset) == 0x40656368) and (ReadWord(file, Offset+4) == 0x6F206F66):
        filename = str(i) + ".bat"
    elif (ReadWord(file, Offset) == 0x504F5309):
        filename = str(i) + ".pos"
    elif (ReadWord(file, Offset) == 0x0D0A6675):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x4C4F4341) and (ReadWord(file, Offset+4) == 0x544F5253):
        filename = str(i) + ".locators"
    elif (ReadWord(file, Offset) == 0x312C2242) and (ReadWord(file, Offset+4) == 0x6174746C):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x66756E63) and (ReadWord(file, Offset+4) == 0x74696F6E):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x52454D20) and (ReadWord(file, Offset+4) == 0x2D2D2047):
        filename = str(i) + ".bat"
    elif (ReadWord(file, Offset) == 0x53554254) and (ReadWord(file, Offset+4) == 0x49544C45):
        filename = str(i) + ".subs.txt"
    elif (ReadWord(file, Offset) == 0x53474F44):
        filename = str(i) + ".sgod"
    elif (ReadWord(file, Offset) == 0x0D0A0D0A):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x4E554D45) and (ReadWord(file, Offset+4) == 0x44474553):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x4E554D43) and (ReadWord(file, Offset+4) == 0x52454449):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x01000000):
        filename = str(i) + ".bin"
    elif (ReadWord(file, Offset) == 0x02000000):
        filename = str(i) + ".bin"
    elif (ReadWord(file, Offset) == 0x4E414D45):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x200D0A2F):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x50415448):
        filename = str(i) + ".bat"
    elif (ReadWord(file, Offset) == 0x0D0A4E41):
        filename = str(i) + ".txt"
    elif (ReadHWord(file, Offset) == 0x2E2E) and (ReadByte(file, Offset+2) == 0x5C):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x54494E54) and (ReadWord(file, Offset+4) == 0x494E473A):
        filename = str(i) + ".tinting.txt"
    elif (ReadWord(file, Offset) == 0x0D0A2066):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x4D4F4449) and (ReadWord(file, Offset+4) == 0x54454D53):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x5343454E) and (ReadWord(file, Offset+4) == 0x453A0909):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x496E7465) and (ReadWord(file, Offset+4) == 0x72666163):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x4C656167) and (ReadWord(file, Offset+4) == 0x75655374):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x5C70726F) and (ReadWord(file, Offset+4) == 0x6A656374):
        filename = str(i) + ".txt"
    elif (ReadHWord(file, Offset) == 0x0D0A):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x5041583A):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x3A204765):
        filename = str(i) + ".bat"
    elif (ReadWord(file, Offset) == 0x6275696C) and (ReadWord(file, Offset+4) == 0x6470616B):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x5363686F) and (ReadWord(file, Offset+4) == 0x6F6C5374):
        filename = str(i) + ".txt"
    elif (ReadWord(file, Offset) == 0x40000000):
        filename = str(i) + ".mih"
    else:
        filename = str(i) + ".bin"

    return filename

def ReadWord(file, Offset):
    file.seek(Offset)
    data = file.read(4)
    word, = struct.unpack(">I", data)
    return word

def ReadHWord(file, Offset):
    file.seek(Offset)
    data = file.read(2)
    word,  = struct.unpack(">H", data)
    return word

def ReadByte(file, Offset):
    file.seek(Offset)
    data = file.read(1)
    word,  = struct.unpack("<B", data)
    return word


def unpackBecArchive(filename, filedir, outFileList, console, demobec=False, debug=False):
    file = open(filename, "rb+")
    header_output = unpackBecArchive2(file, filedir, console, demobec, debug)
    
    headerfilename = filedir + outFileList
    if not os.path.exists(os.path.dirname(headerfilename)) and os.path.dirname(headerfilename):
        os.makedirs(os.path.dirname(headerfilename))
    fheader = open(headerfilename, 'w')
    fheader.write(header_output)

def unpackBecArchive2(file, filedir, console, demobec=False, debug=False):
    output = ""

    RomSections = []
    
    BecHeader = namedtuple('BecHeader', ['FileAlignment', 'NrOfFiles', 'HeaderMagic'])

    file.seek(0x6)
    data = file.read(10)
    header = BecHeader._make(struct.unpack('<HII', data))

    print("Nr of Files in the bec-file: " + str(header.NrOfFiles))
    print("File Alignment: " + str(header.FileAlignment))
    output += hex(header.FileAlignment) + separator + hex(header.NrOfFiles) + separator + hex(header.HeaderMagic) + "\n"

    FileEntry = namedtuple('FileEntry', ['PathHash', 'DataOffset', 'CompDataSize', 'DataSize'])
    for i in range(header.NrOfFiles):
        data = file.read(0x10)
        entry = FileEntry._make(struct.unpack('<IIII', data))

        romSection = RomSection("", "", entry.PathHash, entry.DataOffset, entry.CompDataSize & 0x00FFFFFF, entry.CompDataSize>>24, entry.DataSize, 0, 0)
        RomSections.append(romSection)

    i = 0
    for romSection in RomSections:
        if romSection.compsize > 0: # PS2 version (checksum after zlib file)
            Offset = romSection.address + romSection.compsize
        else: # GC version (checksum after uncompressed file)
            Offset = romSection.address + (header.FileAlignment - 1)
            Offset &= (0x100000000 - header.FileAlignment)
            Offset += romSection.size
        file.seek(Offset)
        data = file.read(8)
        CheckSum1, CheckSum2 = struct.unpack("<II", data)

        Offset = romSection.address + romSection.compsize + (header.FileAlignment - 1)
        if romSection.compsize > 0:
            Offset += 8
        Offset &= (0x100000000 - header.FileAlignment)

        filename = GetFilenameOfFile(file, Offset, romSection.size, romSection.hash, i)
        filename2 = "zlib/" + filename + ".zlib"
		
        if romSection.compsize > 0:
            fByteArray = ReadSection(file, romSection.address, romSection.compsize)
            WriteSectionInFile(fByteArray, filedir, filename2, romSection.compsize)
        else:
            filename2 = "nothing"

        if (console != "xbox") or (romSection.compsize == 0): # xbox doesn't have uncompressed files, so here we uncompress the compressed files
            fByteArray = ReadSection(file, Offset, romSection.size)
            WriteSectionInFile(fByteArray, filedir, filename, romSection.size)
        else:
            fByteArray = ReadSection(file, romSection.address, romSection.compsize)
            fByteArray2 = zlib.decompress(fByteArray)
            WriteSectionInFile(fByteArray2, filedir, filename, romSection.size)
	
        output += filename + separator
        output += filename2 + separator
        output += hex(romSection.hash).rstrip("L") + separator
        output += hex(romSection.address).rstrip("L") + separator
        output += hex(romSection.flags).rstrip("L") + separator
        output += hex(CheckSum1).rstrip("L") + separator + hex(CheckSum2).rstrip("L") + separator #+ "\n"
        output += hex(romSection.size).rstrip("L") + separator + hex(romSection.compsize).rstrip("L") + "\n"

        i += 1
        
    return output



# PACK BEC-ARCHIVE
#####################

RomMap = []


def alignFileSizeWithZeros(file, pos, alignment):
    target = (pos + alignment - 1) & (0x100000000-alignment)
    amount = target - pos
    file.write(b'\0' * amount)

def readFileList(becmap, dir):
    FileAlignment = 0x0
    NrOfFiles = 0x0
    HeaderMagic = 0x0

    with open(becmap) as fin:
        for line in fin:
            words = line.split(separator)
            if len(words) == 3:
                FileAlignment = int(words[0], 16)
                NrOfFiles = int(words[1], 16)
                HeaderMagic = int(words[2], 16)
            else:
                words = line.split(separator) # filename, filename2, hash, offset, flags, checksum, checksum2
                #print(words)
                if len(words) > 3:
                    FileSize = os.path.getsize(dir + "/" + words[0])
                    FileSize2 = 0
                    if words[1] != "nothing":
                        FileSize2 = os.path.getsize(dir + "/" + words[1])
                    RomMap.append(RomSection(words[0], words[1], int(words[2], 16), int(words[3], 16), FileSize2, int(words[4], 16), FileSize, int(words[5], 16), int(words[6], 16))) # filename, filename2, hash?, offset, filesize2, flags?, filesize, checksum?, checksum2?

    return FileAlignment, NrOfFiles, HeaderMagic

def createBecArchive(dir, filename, becmap, console, demobec=False, ignorechecksum=False, debug=False):
    FileAlignment = 0x0
    NrOfFiles = 0x0
    HeaderMagic = 0x0

    FileAlignment, NrOfFiles, HeaderMagic = readFileList(becmap, dir)
    #if (console == "xbox"):
    #    FileAlignment >>= 8
        
    if os.path.dirname(filename) != "":
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
    output_bec = open(filename, 'wb')

	# write header
    version = 0x3 # useChecksumVersion
    if ignorechecksum:
        version = 0x1 # ignoreChecksumVersion
    output_bec.write(struct.pack('<4sHHII', b" ceb", int(version), int(FileAlignment), int(NrOfFiles), int(HeaderMagic)))

    # updated the filesizes
    RomMap.sort(key=operator.attrgetter('address')) # address
    addr = 0x10 + NrOfFiles*0x10 + (FileAlignment - 1)
    addr &= (0x100000000 - FileAlignment)
    diffaddr = 0
    oldaddr = addr
	
    for item in RomMap:
        if item.flags == 2:
            continue
        
        if item.address != addr and diffaddr == 0:
            print("Adr diff: org: " + hex(item.address) + ", new: " + hex(addr) + ", prevaddr: " + hex(oldaddr) + ", " + item.name)
            diffaddr = 1
        oldaddr = addr
        item.new_address = addr

        if (item.compsize > 0):
            addr += item.compsize + 8 + (FileAlignment - 1)
            addr &= (0x100000000 - FileAlignment)

        if (console != "xbox") or (item.compsize == 0): # XBox only uses compressed zlib files, except for really small files
            addr += item.size + (FileAlignment - 1)
            if ((console == "xbox") and (item.size == 0)):
                addr += 8
        if ((item.compsize == 0) and (item.size > 0)) or (console == "gc"):
            addr += 8 # GCExclusive + 8 for checksum being saved here
        addr &= (0x100000000 - FileAlignment)
        if (item.compsize == 0) and (item.size == 0) and (console == "ps2"): # PS2Exclusive
            addr += FileAlignment

    # fix the second instant of some file entries
    for i in range(len(RomMap)):
        if RomMap[i].flags != 0:
            for j in range(len(RomMap)):
                if (i != j) and (RomMap[j].flags == 0) and (RomMap[i].address == RomMap[j].address):
                    RomMap[i].new_address = RomMap[j].new_address
                    RomMap[i].size = RomMap[j].size
    
    RomMap.sort(key=operator.attrgetter('hash'))
    for item in RomMap:
        output_bec.write(struct.pack('<IIII', int(item.hash), int(item.new_address), int(item.compsize & 0xffffff) | (int(item.flags) << 24), int(item.size)))

    alignFileSizeWithZeros(output_bec, output_bec.tell(), FileAlignment)
    
    RomMap.sort(key=operator.attrgetter('address'))
    i = 0
    for item in RomMap:
        if item.flags == 2: # skip files where flag == 2
            continue

        if (item.compsize > 0):
            filepath2 = dir + "/" + item.compname
            filedata2 = bytearray(open(filepath2, "rb").read())
            output_bec.write(filedata2)
            output_bec.write(struct.pack('<II', int(item.checksum), int(item.checksum2))) # checksum? PS2Exclusive
            alignFileSizeWithZeros(output_bec, output_bec.tell(), FileAlignment)

        if (console != "xbox") or (item.compsize == 0):
            filepath = dir + "/" + item.name
            file = open(filepath, "rb")
            filedata = bytearray(file.read())
            file.close()
            output_bec.write(filedata)
            if ((console == "xbox") and (item.size == 0)):
                output_bec.write(struct.pack('<II', item.checksum, item.checksum2)) # checksum?
        if ((item.compsize == 0) and (item.size > 0)) or (console == "gc"):
            output_bec.write(struct.pack('<II', item.checksum, item.checksum2)) # checksum? GCExclusive
		
        alignFileSizeWithZeros(output_bec, output_bec.tell(), FileAlignment)
			
        if (item.compsize == 0) and (item.size == 0) and (console == "ps2"):
            output_bec.write(b'\0' * FileAlignment) # write dvd filler material into archive PS2Exclusive

        output_bec.flush()
        
        i += 1
        if (i % 2500) == 0:
            print("write progress... " + str(i) + "/" + str(len(RomMap)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-pack', action='store', nargs=3, type=str, metavar=("inputDir", "outputFile", "becFilelist"), help="pack files into a bec-archive")
    group.add_argument('-unpack', action='store', nargs=3, type=str, metavar=("inputFile", "outputDir", "becFilelist"), help="unpack files from a bec-archive")
    #parser.add_argument("--gc", action="store_true", help="activate GC mode") # switch between PS2 and GC Mode, the bec-formats they use don't seem completely compatible
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--gc', action='store_true', help="activate GC mode")
    group.add_argument('--ps2', action='store_true')
    group.add_argument('--xbox', action='store_true')
    args = parser.parse_args()

    start = time.time()
    debug = True
    console = "ps2"
    if args.gc:
        console = "gc"
    if args.ps2:
        console = "ps2"
    if args.xbox:
        console = "xbox"

    if args.pack:
        createBecArchive(args.pack[0], args.pack[1], args.pack[2], console, debug)
    if args.unpack:
        unpackBecArchive(args.unpack[0], args.unpack[1], args.unpack[2], console, debug)

    if debug:
        elapsed_time_fl = (time.time() - start)
        print("passed time: " + str(elapsed_time_fl))
