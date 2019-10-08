# -*- coding: utf-8 -*-
"""
---
"""

import os
import sys
import operator
import struct
import hashlib
import gladiushashes


class RomSection():
    def __init__(self, name, address, fileID, size):
        self.name = name
        self.address = address
        self.fileID = fileID
        self.size = size

RomMap = []

def addRomSection(name, address, size, fileID=-1):
    if size > 0:
        RomMap.append(RomSection(name, address, fileID, size))
    return None

def alignAdr(adr, alignVal):
    if (adr & (alignVal-1)) != 0:
        adr = adr & 0x100000000-alignVal
        adr += alignVal
    return adr

def getOutputRomMap(file, filedir):
    output = ""
    old_address = 0
    
    RomMap.sort(key=operator.attrgetter('address'))
    for item in RomMap:
        if old_address != item.address:
            WriteSectionInFile(file, filedir, "Unknown_" + hex(old_address) + ".bin", old_address, item.address-old_address)
            output += hex(old_address) + " " + "/Unknown_" + hex(old_address) + ".bin" + " " + hex(-1) + " " + hex(item.address-old_address) + "\n"
        output += hex(item.address) + " " + str(item.name) + " " + hex(item.fileID) + " " + hex(item.size) + "\n"
        old_address = alignAdr(item.address + item.size, 4)
    
    return output

def getOutputRomMapFileID():
    output = ""
    
    RomMap.sort(key=operator.attrgetter('fileID'))
    for item in RomMap:
        output += hex(item.fileID) + " " + str(item.name) + " "+ hex(item.address) + " " + hex(item.size) + "\n"
    
    return output


class DirName():
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

DirNames = []

def getDirPath(FileID):
    string = ""
    for dir in DirNames:
        if (FileID >= dir.start) & (FileID < dir.end):
            string += dir.name + "/"
    return string

def addDirName(name, start, end):
    DirNames.append(DirName(name, start, end))



def GetFileSize(file):
    file.seek(0, os.SEEK_END)
    return file.tell()

def WriteSectionInFile(file, dirname, filename, addr, size):
    if not os.path.exists(os.path.dirname(dirname + filename)):
        os.makedirs(os.path.dirname(dirname + filename))
        
    file.seek(addr)
    fByteArray = file.read(size)
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

def ReadByte(file, Offset):
    file.seek(Offset)
    data = file.read(1)
    word,  = struct.unpack("<B", data)
    return word

def ReadString(file, Offset, size):
    file.seek(Offset)
    string = ""
    for i in range(size):
        byte = bytearray(file.read(1))
        if(byte[0] != 0):
            string += chr(byte[0])
    return string

def ReadString0(file, Offset, size):
    file.seek(Offset)
    string = ""
    bytes = bytearray(file.read(size))
    for i in range(size):
        if(bytes[i] != 0):
            string += chr(bytes[i])
        else:
            break
    return string

def ReadHexString(file, Offset, size):
    file.seek(Offset)
    string = ""
    for i in range(size):
        byte = bytearray(file.read(1))
        string += ("%02x" % byte[0]) # {:02x}'.format(byte[0])
    return string



def diagnose(filename="baserom.nds", filedir="", outFileList="", debug=False):
    base_address = 0x0
    file = open(filename, "rb+")

    header_output = ""
    header_output += filename + "\n"
    header_output += "FileSize:    " + hex(GetFileSize(file)) + "\n"
    
	
    header_output += "\nGame Code:         " + str(ReadString(file, 0x0, 0x4))
    header_output += "\nMaker Code:        " + str(ReadString(file, 0x4, 0x2))
    header_output += "\nDVD Magic Word:    0x" + str(ReadHexString(file, 0x1c, 0x4))
    header_output += "\nGame Name:         " + str(ReadString(file, 0x20, 0x3e0))
    WriteSectionInFile(file, filedir, "boot.bin", 0x0, 0x440)
    addRomSection("/boot.bin", 0x0, 0x440)
    WriteSectionInFile(file, filedir, "bi2.bin", 0x440, 0x2000)
    addRomSection("/bi2.bin", 0x440, 0x2000)
    
    apploader_entry = ReadWord(file, 0x2440+0x10)
    header_output += "\nApploader Entrypoint: " + hex(apploader_entry)
    appsize = ReadWord(file, 0x2440+0x14) # Apploader Size
    appsize += ReadWord(file, 0x2440+0x18) # Trailer Size
    append = alignAdr(0x2440 + appsize, 0x100)
    WriteSectionInFile(file, filedir, "appldr.bin", 0x2440, appsize)
    addRomSection("/appldr.bin", 0x2440, append-0x2440)
    
    fst_offset = ReadWord(file, base_address+0x0+0x424)
    fst_size = ReadWord(file, base_address+0x0+0x428)
    WriteSectionInFile(file, filedir, "fst.bin", fst_offset, fst_size)
    addRomSection("/fst.bin", fst_offset, fst_size)
    
    header_output += DolFSdiagnose(file, ReadWord(file, base_address+0x0+0x420), filedir, debug)
    
    header_output += RomFSdiagnose(file, ReadWord(file, base_address+0x0+0x424), filedir, debug)
    
    header_output += "\n\n"
    FileList = getOutputRomMap(file, filedir) + "\n"
    header_output += FileList
    header_output += getOutputRomMapFileID()
    
    if outFileList != "":
        outFileList = filedir + outFileList
        if not os.path.exists(os.path.dirname(outFileList)) and os.path.dirname(outFileList):
            os.makedirs(os.path.dirname(outFileList))
        fFileList = open(outFileList, 'w')
        fFileList.write(FileList)
    
    headerfilename = filedir + "_Header.txt"
    if not os.path.exists(os.path.dirname(headerfilename)) and os.path.dirname(headerfilename):
        os.makedirs(os.path.dirname(headerfilename))
    fheader = open(headerfilename, 'w')
    fheader.write(header_output)


def RomFSdiagnose(file, base_address, filedir="", debug=False):
    output = ""
    
    output += RomFS_RootDirdiagnose(file, base_address, 0x0, "", debug)
    dirs = ""
    num_entries = ReadWord(file, base_address+0x8)
    for i in range(num_entries):
        file_offset = 0xc*i
        print("RomFS: " + str(i))
        
        if(ReadByte(file, base_address+file_offset) == 1):
            dirs = RomFS_Dirdiagnose(file, base_address, file_offset, num_entries*0xc, "", debug) + "/"
        elif(ReadByte(file, base_address+file_offset) == 0):
            output += RomFS_Filediagnose(file, base_address, file_offset, num_entries*0xc, getDirPath(i), filedir, debug)
        
    return output


def RomFS_RootDirdiagnose(file, base_address, offset, path, debug=False):
    output = ""
    
    flags = ReadByte(file, base_address+0x0) # 0: file, 1: directory
    offset_string = (ReadWord(file, base_address+0x0))&0xffffff
    parent_offset = ReadWord(file, base_address+0x4)
    num_entries = ReadWord(file, base_address+0x8)
    
    output = "\nRootDir: " + hex(offset_string) + " - " + hex(parent_offset) + " - " + hex(num_entries)
    
    return output


def RomFS_Dirdiagnose(file, base_address, offset, string_table, path, debug=False):
    output = ""
    
    flags = ReadByte(file, base_address+offset+0x0) # 0: file, 1: directory
    offset_string = ((ReadWord(file, base_address+offset+0x0))&0xffffff) + string_table
    string = ReadString0(file, base_address+offset_string, 0x20)
    parent_offset = ReadWord(file, base_address+offset+0x4)
    next_offset = ReadWord(file, base_address+offset+0x8)
    
    if offset == 0:
        string = ""
    
    #output = "\nDir: " + hex(offset_string) + " (" + string + ") - " + hex(parent_offset) + " - " + hex(next_offset)
    output = string
    
    print "dir name at: " + hex(base_address+offset_string)
    print "offset: " + hex(offset/0xc) + " (parent: " + hex(parent_offset) + "), (next: " + hex(next_offset) + "), " + output
    addDirName(string, offset/0xc, next_offset)
    
    return output


def RomFS_Filediagnose(file, base_address, offset, string_table, path, filedir="", debug=False):
    output = ""
    
    flags = ReadByte(file, base_address+offset+0x0) # 0: file, 1: directory
    offset_string = ((ReadWord(file, base_address+offset+0x0))&0xffffff) + string_table
    string = ReadString0(file, base_address+offset_string, 0x20)
    file_offset = ReadWord(file, base_address+offset+0x4)
    file_length = ReadWord(file, base_address+offset+0x8)
    if string == "":
        string = "Unknown_" + hex(file_offset) + ".bin"
    print "file name at: " + hex(base_address+offset_string)
    
    addRomSection(path + string, file_offset, file_length, offset/0xc)
    
    WriteSectionInFile(file, (filedir + path).replace("//", "/"), string.replace("//", "/"), file_offset, file_length)
    
    return output


def DolFSdiagnose(file, base_address, filedir="", debug=False):
    header_output = "\n"
    
    TextPos = []
    DataPos = []
    TextMem = []
    DataMem = []
    TextSize = []
    DataSize = []
    TotSize = 0x100
    for i in range(6):
        TextPos += [ReadWord(file, base_address+0x0+0x4*i)]
        TextMem += [ReadWord(file, base_address+0x48+0x4*i)]
        TextSize += [ReadWord(file, base_address+0x90+0x4*i)]
        TotSize += TextSize[i]
    
    for i in range(6):
        header_output += "Text " + hex(TextPos[i]) + ":   " + hex(TextMem[i]) + " - " + hex(TextSize[i]) + "\n"
    
    for i in range(10):
        DataPos += [ReadWord(file, base_address+0x1c+0x4*i)]
        DataMem += [ReadWord(file, base_address+0x64+0x4*i)]
        DataSize += [ReadWord(file, base_address+0xac+0x4*i)]
        TotSize += DataSize[i]
    
    for i in range(10):
        header_output += "Data " + hex(DataPos[i]) + ":   " + hex(DataMem[i]) + " - " + hex(DataSize[i]) + "\n"
    
    header_output += "\n"
    
    for i in range(6):
        WriteSectionInFile(file, filedir + "code/", "Text_" + hex(TextMem[i]) + ".bin", base_address+TextPos[i], TextSize[i])
    
    for i in range(10):
        WriteSectionInFile(file, filedir + "code/", "Data_" + hex(DataMem[i]) + ".bin", base_address+DataPos[i], DataSize[i])
    
    TotSize = alignAdr(TotSize, 0x100)
    WriteSectionInFile(file, filedir, "bootfile.dol", base_address, TotSize)
    addRomSection("/bootfile.dol", base_address, TotSize)
    
    return header_output


if __name__ == "__main__":
    filename = ""
    outdir = ""
    outFileList = ""
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-i":
            filename = sys.argv[i+1]
            outdir = os.path.splitext(filename)[0]
            i += 2
        elif sys.argv[i] == "-of":
            outdir = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-filelist":
            outFileList = sys.argv[i+1]
            i += 2
    
    diagnose(filename, outdir, outFileList)
