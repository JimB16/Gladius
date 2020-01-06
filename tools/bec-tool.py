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


# PACK BEC-ARCHIVE
#####################

MAX_NR_OF_THREADS = 1
file_queue = queue.Queue()


def ReadSection(file, addr, size, debug=False):
    file.seek(addr)
    return file.read(size)

def WriteSectionInFile(fByteArray, dirname, filename, addr, size, debug=False):
    filename2 = dirname + filename
    if not os.path.exists(os.path.dirname(filename2)):
        os.makedirs(os.path.dirname(filename2))
    outFile = open(filename2, 'wb')
    outFile.write(fByteArray)
    outFile.flush()
    outFile.close()

    print("Write out file " + filename2)

def file_worker():
    while True:
        item = file_queue.get()
        if item is None:
            break
        fByteArray, dirname, filename, addr, size = item
        WriteSectionInFile(fByteArray, dirname, filename, addr, size)
        file_queue.task_done()

def GetFilenameOfFile(file, addr, size, pathhash, i, debug=False):
    if pathhash in gladiushashes.pathhashes:
        outfilename = gladiushashes.pathhashes[pathhash]
    else:
        file.seek(addr)
        fByteArray = file.read(size)
        m = hashlib.md5()
        m.update(fByteArray)
        md5 = m.hexdigest()
        if md5 in gladiushashes.hashes:
            outfilename = gladiushashes.hashes[md5]
        else:
            outfilename = GetNumberedFilenameOfFile(file, addr, i)
	
    return outfilename

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


def diagnose(filename, filedir, outFileList, debug=False):
    file = open(filename, "rb+")
    header_output = diagnose2(file, filedir, debug)
    
    headerfilename = filedir + outFileList
    if not os.path.exists(os.path.dirname(headerfilename)) and os.path.dirname(headerfilename):
        os.makedirs(os.path.dirname(headerfilename))
    fheader = open(headerfilename, 'w')
    fheader.write(header_output)

def diagnose2(file, filedir, debug=False):
    output = ""
    
    file.seek(0x6)
    data = file.read(10)
    BecHeader = namedtuple('BecHeader', ['FileAlignment', 'NrOfFiles', 'HeaderMagic'])
    header = BecHeader._make(struct.unpack('<HII', data))
    print("Nr of Files in the bec-file: " + str(header.NrOfFiles))
    output += hex(header.FileAlignment) + " " + hex(header.NrOfFiles) + " " + hex(header.HeaderMagic) + "\n"
    
    PathHash = []
    DataOffset = []
    OffsetCorrection = []
    Data3 = []
    DataSize = []
    CheckSums1 = []
    CheckSums2 = []
    FileEntry = namedtuple('FileEntry', ['PathHash', 'DataOffset', 'correction0', 'correction1', 'correction2', 'Data3', 'DataSize'])
    for i in range(header.NrOfFiles):
        data = file.read(0x10) # file.seek(0x10+0x10*i)
        entry = FileEntry._make(struct.unpack('<IIBBBBI', data))

        PathHash += [entry.PathHash]
        DataOffset += [entry.DataOffset]
        correction = (entry.correction2 << 16) + (entry.correction1 << 8) + (entry.correction0 << 0)
        OffsetCorrection += [correction]
        Data3 += [entry.Data3] # 0 or 2
        DataSize += [entry.DataSize]
	
    for i in range(header.NrOfFiles):
        if OffsetCorrection[i] > 0: # PS2 version (checksum after zlib file)
            Offset = DataOffset[i] + OffsetCorrection[i]
        else: # GC version (checksum after uncompressed file)
            Offset = DataOffset[i] + (header.FileAlignment - 1)
            Offset &= (0x100000000 - header.FileAlignment)
            Offset += DataSize[i]
        file.seek(Offset)
        data = file.read(8)
        CheckSum1, CheckSum2 = struct.unpack("<II", data)
        CheckSums1 += [CheckSum1]
        CheckSums2 += [CheckSum2]
    
    for i in range(header.NrOfFiles):
        Offset = DataOffset[i] + OffsetCorrection[i] + (header.FileAlignment - 1)
        if OffsetCorrection[i] > 0:
            Offset += 8
        Offset &= (0x100000000 - header.FileAlignment)
		
        filename = GetFilenameOfFile(file, Offset, DataSize[i], PathHash[i], i)
        fByteArray = ReadSection(file, Offset, DataSize[i])
        WriteSectionInFile(fByteArray, filedir, filename, Offset, DataSize[i])
        #file_queue.put((fByteArray, filedir, filename, Offset, DataSize[i],))
		
        filename2 = "zlib/" + filename + ".zlib"
        if OffsetCorrection[i] > 0:
            fByteArray = ReadSection(file, DataOffset[i], OffsetCorrection[i])
            WriteSectionInFile(fByteArray, filedir, filename2, DataOffset[i], OffsetCorrection[i])
            #file_queue.put((fByteArray, filedir, filename2, DataOffset[i], OffsetCorrection[i],))
        else:
            filename2 = "nothing"
	
        output += "\"" + filename + "\" " + "\"" + filename2 + "\" " + hex(PathHash[i]).rstrip("L") + " " + hex(DataOffset[i]).rstrip("L") + " " + hex(OffsetCorrection[i]).rstrip("L") + " " + hex(Data3[i]).rstrip("L") + " " + hex(DataSize[i]).rstrip("L") + " " + hex(CheckSums1[i]).rstrip("L") + " " + hex(CheckSums2[i]).rstrip("L") + "\n"

    for i in range(MAX_NR_OF_THREADS):
        file_queue.put(None)
        
    return output



# UNPACK BEC-ARCHIVE
#####################

RomMap = []

class RomSection():
    def __init__(self, name, name2, hash, address, size2, flags, size, checksum, checksum2):
        self.name = name
        self.name2 = name2
        self.hash = hash
        self.address = address
        self.new_address = address
        self.flags = flags
        self.size = size
        self.size2 = size2
        self.checksum = checksum
        self.checksum2 = checksum2

def addRomSection(name, name2, hash, address, size2, flags, size, checksum, checksum2): # filename, hash?, offset, offsetcorrection, flags?, filesize, checksum?
    RomMap.append(RomSection(name, name2, hash, address, size2, flags, size, checksum, checksum2))

def alignFileSizeWithZeros(file, pos, alignment):
    target = (pos + alignment - 1) & (0x100000000-alignment)
    amount = target - pos
    file.write(b'\0' * amount)


def createBecArchive(dir, filename, becmap, gc, debug=False):
    filealignment = 0x0
    NrOfFiles = 0x0
    HeaderMagic = 0x0
	
    with open(becmap) as fin:
        for line in fin:
            words = line.split()
            if len(words) == 3:
                filealignment = int(words[0], 16)
                NrOfFiles = int(words[1], 16)
                HeaderMagic = int(words[2], 16)
            else:
                words_temp = line.split("\"") # filename, filename2
                words = [words_temp[1]] + [words_temp[3]] + words_temp[4].split() # ?, offset, flags?, filesize
                #print(words)
                if len(words) == 9:
                    FileSize = os.path.getsize(dir + "/" + words[0])
                    FileSize2 = 0
                    if words[1] != "nothing":
                        FileSize2 = os.path.getsize(dir + "/" + words[1])
                    addRomSection(words[0], words[1], int(words[2], 16), int(words[3], 16), FileSize2, int(words[5], 16), FileSize, int(words[7], 16), int(words[8], 16)) # filename, filename2, hash?, offset, filesize2, flags?, filesize, checksum?, checksum2?
        
    if os.path.dirname(filename) != "":
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
    output_rom = open(filename, 'wb')

	# write header
    output_rom.write(struct.pack('<4sHHII', b" ceb", int(0x3), int(filealignment), int(NrOfFiles), int(HeaderMagic)))

    # updated the filesizes
    RomMap.sort(key=operator.attrgetter('address')) # address
    #addr = RomMap[0].address
    addr = 0x10 + NrOfFiles*0x10 + (filealignment - 1)
    addr &= (0x100000000 - filealignment)
    diffaddr = 0
    oldaddr = addr
	
    for item in RomMap:
        if item.flags != 0:
            continue
        
        #item.size = os.path.getsize(dir + "/" + item.name)
        if item.address != addr and diffaddr == 0:
            print("Adr diff: org: " + hex(item.address) + ", new: " + hex(addr) + ", prevaddr: " + hex(oldaddr))
            diffaddr = 1
        oldaddr = addr
        item.new_address = addr
        if item.size2 > 0:
            addr += item.size2 + 8 + (filealignment - 1)
            addr &= (0x100000000 - filealignment)
        addr += item.size + (filealignment - 1)
        if ((item.size2 == 0) and (item.size > 0)) or (gc == 1):
            addr += 8 # GCExclusive + 8 for checksum being saved here
        addr &= (0x100000000 - filealignment)
        if (item.size2 == 0) and (item.size == 0) and (gc == 0): # PS2Exclusive
            addr += filealignment

    # fix the second instant of some file entries
    for i in range(len(RomMap)):
        if RomMap[i].flags != 0:
            for j in range(len(RomMap)):
                if (i != j) and (RomMap[j].flags == 0) and (RomMap[i].address == RomMap[j].address):
                    RomMap[i].new_address = RomMap[j].new_address
                    RomMap[i].size = RomMap[j].size
    
    RomMap.sort(key=operator.attrgetter('hash')) # address
    for item in RomMap:
        output_rom.write(struct.pack('<II', int(item.hash), int(item.new_address)))
        output_rom.write(struct.pack('<BBB', int((item.size2 >> 0) & 0xff), int((item.size2 >> 8) & 0xff), int((item.size2 >> 16) & 0xff)))
        output_rom.write(struct.pack('<BI', int(item.flags), int(item.size)))

    alignFileSizeWithZeros(output_rom, output_rom.tell(), filealignment)
    
    RomMap.sort(key=operator.attrgetter('address')) # address
    i = 0
    for item in RomMap:
        if item.flags != 0: # skip files where flag == 2
            continue

        if item.size2 > 0:
            filepath2 = dir + "/" + item.name2
            filedata2 = bytearray(open(filepath2, "rb").read())
            output_rom.write(filedata2)
            output_rom.write(struct.pack('<II', int(item.checksum), int(item.checksum2))) # checksum? PS2Exclusive
            alignFileSizeWithZeros(output_rom, output_rom.tell(), filealignment)
		
        filepath = dir + "/" + item.name
        file = open(filepath, "rb")
        filedata = bytearray(file.read())
        file.close()
        output_rom.write(filedata)
        if ((item.size2 == 0) and (item.size > 0)) or (gc == 1):
            output_rom.write(struct.pack('<II', item.checksum, item.checksum2)) # checksum? GCExclusive
		
        alignFileSizeWithZeros(output_rom, output_rom.tell(), filealignment)
			
        if (item.size2 == 0) and (item.size == 0) and (gc == 0):
            output_rom.write(b'\0' * filealignment) # write dvd filler material into archive PS2Exclusive

        output_rom.flush()
        
        i += 1
        if (i % 2500) == 0:
            print("write progress... " + str(i) + "/" + str(len(RomMap)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-pack', action='store', nargs=3, type=str, metavar=("inputDir", "outputFile", "becFilelist"), help="pack files into a bec-archive")
    group.add_argument('-unpack', action='store', nargs=3, type=str, metavar=("inputFile", "outputDir", "becFilelist"), help="unpack files from a bec-archive")
    parser.add_argument("--gc", action="store_true", help="activate GC mode") # switch between PS2 and GC Mode, the bec-formats they use don't seem completely compatible
    args = parser.parse_args()

    start = time.time()
    debug = True
    gc = 0
    if args.gc:
        gc = 1

    if args.pack:
        createBecArchive(args.pack[0], args.pack[1], args.pack[2], gc, debug)
    if args.unpack:
        diagnose(args.unpack[0], args.unpack[1], args.unpack[2], debug)

    if debug:
        elapsed_time_fl = (time.time() - start)
        print("passed time: " + str(elapsed_time_fl))
