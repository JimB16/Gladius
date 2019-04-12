# -*- coding: utf-8 -*-

import os
import sys
import struct
import hashlib
import gladiushashes


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
        
    print("Write section in file " + filename2 + " " + m.hexdigest())
	
    return outfilename

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


def diagnose(filename="baseiso.iso", filedir="", outFileList="", debug=False):
    file = open(filename, "rb+")

    header_output = ""
    header_output += diagnose2(file, filedir, debug)
    
    headerfilename = filedir + outFileList
    if not os.path.exists(os.path.dirname(headerfilename)) and os.path.dirname(headerfilename):
        os.makedirs(os.path.dirname(headerfilename))
    fheader = open(headerfilename, 'w')
    fheader.write(header_output)

def diagnose2(file2, filedir="", debug=False):
    output = ""
    
    file2.seek(0x6)
    data = file2.read(10)
    FileAlignment, NrOfFiles, HeaderMagic = struct.unpack("<HII", data)
    print("Nr of Files: " + str(NrOfFiles))
    output += hex(FileAlignment) + " " + hex(NrOfFiles) + " " + hex(HeaderMagic) + "\n"
    
    DataPos = []
    DataOffset = []
    OffsetCorrection = []
    Data3 = []
    DataSize = []
    CheckSums1 = []
    CheckSums2 = []
    for i in range(NrOfFiles):
        #file2.seek(0x10+0x10*i)
        data = file2.read(0x10)
        DataPos_, DataOffset_, correction0, correction1, correction2, Data3_, DataSize_ = struct.unpack("<IIBBBBI", data)

        DataPos += [DataPos_]
        DataOffset += [DataOffset_]
        correction = (correction2 << 16) + (correction1 << 8) + (correction0 << 0)
        OffsetCorrection += [correction]
        Data3 += [Data3_] # 0 or 2
        DataSize += [DataSize_]
	
    for i in range(NrOfFiles):
        if OffsetCorrection[i] > 0: # PS2 version (checksum after zlib file)
            Offset = DataOffset[i] + OffsetCorrection[i]
        else: # GC version (checksum after uncompressed file)
            Offset = DataOffset[i] + (FileAlignment - 1)
            Offset &= (0x100000000 - FileAlignment)
            Offset += DataSize[i]
        file2.seek(Offset)
        data = file2.read(8)
        CheckSum1, CheckSum2 = struct.unpack("<II", data)
        CheckSums1 += [CheckSum1]
        CheckSums2 += [CheckSum2]
    
    filename = ""
    for i in range(NrOfFiles): # NrOfFiles
        Offset = DataOffset[i] + OffsetCorrection[i] + (FileAlignment - 1)
        if OffsetCorrection[i] > 0:
            Offset += 8
        Offset &= (0x100000000 - FileAlignment)

        if ReadHWord(file2, Offset) == 0x2f2f:
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x0D0A2F2F):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x0D0A0D0A) and (ReadHWord(file2, Offset+4) == 0x2F2F):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x436F7079) and (ReadWord(file2, Offset+4) == 0x72696768):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x56455253):
            filename = str(i) + ".vers"
        elif (ReadWord(file2, Offset) == 0x50545450):
            filename = str(i) + ".pttp"
        elif (ReadWord(file2, Offset) == 0x50414B31):
            filename = str(i) + ".pak1"
        elif (ReadWord(file2, Offset) == 0x23233832) and (ReadWord(file2, Offset+4) == 0x32300D0A):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x1D200000):
            filename = str(i) + ".bin"
        elif (ReadWord(file2, Offset) == 0x504D5332):
            filename = str(i) + ".pms2"
        elif (ReadWord(file2, Offset) == 0x40656368) and (ReadWord(file2, Offset+4) == 0x6F206F66):
            filename = str(i) + ".bat"
        elif (ReadWord(file2, Offset) == 0x504F5309):
            filename = str(i) + ".pos"
        elif (ReadWord(file2, Offset) == 0x0D0A6675):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x4C4F4341) and (ReadWord(file2, Offset+4) == 0x544F5253):
            filename = str(i) + ".locators"
        elif (ReadWord(file2, Offset) == 0x312C2242) and (ReadWord(file2, Offset+4) == 0x6174746C):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x66756E63) and (ReadWord(file2, Offset+4) == 0x74696F6E):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x52454D20) and (ReadWord(file2, Offset+4) == 0x2D2D2047):
            filename = str(i) + ".bat"
        elif (ReadWord(file2, Offset) == 0x53554254) and (ReadWord(file2, Offset+4) == 0x49544C45):
            filename = str(i) + ".subs.txt"
        elif (ReadWord(file2, Offset) == 0x53474F44):
            filename = str(i) + ".sgod"
        elif (ReadWord(file2, Offset) == 0x0D0A0D0A):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x4E554D45) and (ReadWord(file2, Offset+4) == 0x44474553):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x4E554D43) and (ReadWord(file2, Offset+4) == 0x52454449):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x01000000):
            filename = str(i) + ".bin"
        elif (ReadWord(file2, Offset) == 0x02000000):
            filename = str(i) + ".bin"
        elif (ReadWord(file2, Offset) == 0x4E414D45):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x200D0A2F):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x50415448):
            filename = str(i) + ".bat"
        elif (ReadWord(file2, Offset) == 0x0D0A4E41):
            filename = str(i) + ".txt"
        elif (ReadHWord(file2, Offset) == 0x2E2E) and (ReadByte(file2, Offset+2) == 0x5C):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x54494E54) and (ReadWord(file2, Offset+4) == 0x494E473A):
            filename = str(i) + ".tinting.txt"
        elif (ReadWord(file2, Offset) == 0x0D0A2066):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x4D4F4449) and (ReadWord(file2, Offset+4) == 0x54454D53):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x5343454E) and (ReadWord(file2, Offset+4) == 0x453A0909):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x496E7465) and (ReadWord(file2, Offset+4) == 0x72666163):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x4C656167) and (ReadWord(file2, Offset+4) == 0x75655374):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x5C70726F) and (ReadWord(file2, Offset+4) == 0x6A656374):
            filename = str(i) + ".txt"
        elif (ReadHWord(file2, Offset) == 0x0D0A):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x5041583A):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x3A204765):
            filename = str(i) + ".bat"
        elif (ReadWord(file2, Offset) == 0x6275696C) and (ReadWord(file2, Offset+4) == 0x6470616B):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x5363686F) and (ReadWord(file2, Offset+4) == 0x6F6C5374):
            filename = str(i) + ".txt"
        elif (ReadWord(file2, Offset) == 0x40000000):
            filename = str(i) + ".mih"
        else:
            filename = str(i) + ".bin"
		
        filename = WriteSectionInFile(file2, filedir, filename, Offset, DataSize[i])
		
        filename2 = "zlib/" + filename + ".zlib"
        if OffsetCorrection[i] > 0:
            filename2 = WriteSectionInFile(file2, filedir, filename2, DataOffset[i], OffsetCorrection[i])
        else:
            filename2 = "nothing"
	
        output += filename + " " + filename2 + " " + hex(DataPos[i]) + " " + hex(DataOffset[i]) + " " + hex(OffsetCorrection[i]) + " " + hex(Data3[i]) + " " + hex(DataSize[i]) + " " + hex(CheckSums1[i]) + " " + hex(CheckSums2[i]) + "\n"
        
    return output

        
if __name__ == "__main__":
    HelpText = "usage: unpack_bec.py -i InputFile -o OutputFolder -filelist OutputFileList"
    filename = ""
    outdir = ""
    outFileList = "bec_info.txt"
    
    i = 1
    if (len(sys.argv) != 7) or (len(sys.argv) != 7):
        print("Error: wrong number of arguments")
        print(HelpText)
        sys.exit()
    while i < len(sys.argv):
        if sys.argv[i] == "-help":
            print(HelpText)
            sys.exit()
        elif sys.argv[i] == "-i":
            filename = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-o":
            outdir = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-filelist":
            outFileList = sys.argv[i+1]
            i += 2

    print('unpacking ' + filename + "...")
    diagnose(filename, outdir, outFileList)
