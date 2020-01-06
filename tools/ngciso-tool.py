# -*- coding: utf-8 -*-

import os
import sys
import struct
import operator
import argparse


# UNPACK NGC ISO
#################

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

def writeSectionsOutOfIso(file, filedir):
    output = ""
    old_address = 0
    
    RomMap.sort(key=operator.attrgetter('address'))
    for item in RomMap:
        if old_address != item.address:
            WriteSectionInFile(file, filedir, "Unknown_" + hex(old_address) + ".bin", old_address, item.address-old_address)
            output += hex(old_address) + " " + "/Unknown_" + hex(old_address) + ".bin" + " " + hex(int(-1)) + " " + hex(item.address-old_address) + "\n"
        output += hex(item.address) + " " + str(item.name) + " " + hex(int(item.fileID)) + " " + hex(item.size) + "\n"
        old_address = alignAdr(item.address + item.size, 4)
    
    return output

def getOutputRomMapFileID():
    output = ""
    
    RomMap.sort(key=operator.attrgetter('fileID'))
    for item in RomMap:
        output += hex(int(item.fileID)) + " " + str(item.name) + " "+ hex(item.address) + " " + hex(item.size) + "\n"
    
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
    file.seek(addr)
    fByteArray = file.read(size)

    filename2 = dirname + filename
	
    if not os.path.exists(os.path.dirname(filename2)):
        os.makedirs(os.path.dirname(filename2))
    f = open(filename2, 'wb')
    f.write(fByteArray)
    f.flush()
    f.close()
        
    print("Write section in file " + filename2)
	
    return filename

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



def diagnose(filename, filedir, outFileList, debug=False):
    file = open(filename, "rb+")

    header_output = filename + "\n"
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
    
    fst_offset = ReadWord(file, 0x424)
    fst_size = ReadWord(file, 0x428)
    WriteSectionInFile(file, filedir, "fst.bin", fst_offset, fst_size)
    addRomSection("/fst.bin", fst_offset, fst_size)
    
    header_output += DolFSdiagnose(file, ReadWord(file, 0x420), filedir, debug)
    header_output += RomFSdiagnose(file, ReadWord(file, 0x424), filedir, debug)
    
    header_output += "\n\n"
    FileList = writeSectionsOutOfIso(file, filedir) + "\n"
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

    output = string
    
    print("dir name at: " + hex(base_address+offset_string))
    print("offset: " + hex(int(offset/0xc)) + " (parent: " + hex(parent_offset) + "), (next: " + hex(next_offset) + "), " + output)
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
    print("file name at: " + hex(base_address+offset_string))
    
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



# PACK NGC ISO
###############

class fstDir():
    def __init__(self, name, flag, FileID=0, FileSize=0):
        self.name = name
        self.lower = name.lower()
        self.subDirs = []
        self.Files = []
        self.flag = flag
        self.FileID = FileID
        self.FileSize = FileSize
        self.offset = 0

    def getSubDir(self, name):
        for dir in self.subDirs:
            if dir.name == name:
                return dir
        return None

    def getFile(self, name):
        for file in self.Files:
            if file == name:
                return name
        return None

    def addSubDir(self, name):
        subDir = self.getSubDir(name)
        if subDir == None:
            self.subDirs.append(fstDir(name, 1))
        self.subDirs = sorted(self.subDirs, key=lambda fstDir: fstDir.lower.replace("_", "}"))
        return self.getSubDir(name)

    def addFile(self, name, FileID, FileSize):
        subDir = self.getSubDir(name)
        if subDir == None:
            self.subDirs.append(fstDir(name, 0, FileID, FileSize))
        self.subDirs = sorted(self.subDirs, key=lambda fstDir: fstDir.lower.replace("_", "}"))
        return self.getSubDir(name)

    def printDir(self, offset):
        string = offset + self.name + " " + hex(self.getNrOfEntries()) + " " + hex(self.FileID) + " " + hex(self.offset) + "\n"
        for i in self.subDirs:
            string += i.printDir(offset + self.name + "/")
        for i in self.Files:
            string += offset + self.name + "/" + i + "\n"
        return string

    def createFST(self, string_table_length, parentID, ownID):
        if self.FileID == -0x1:
            return ([], "")
        
        Word2 = 0
        Word3 = 0
        string = ""
        if self.name != "":
            string += self.name + "\0"
            if self.flag == 0: # file
                Word3 = self.FileSize
                Word2 = self.offset
            else: # directory
                Word3 = ownID + self.getNrOfEntries()+1 # next_offset
                Word2 = parentID # parent_FileID
        else: # root
            Word3 = self.getNrOfEntries()+1
        
        FST = [self.flag<<24|string_table_length, Word2, Word3]
        
        n = 0
        for i in self.subDirs:
            res = i.createFST(string_table_length + len(string), ownID, ownID+n+1)
            FST += res[0]
            string += res[1]
            if res[1] != "":
                n += 1 + i.getNrOfEntries()
        
        return (FST, string)

    def getNrOfEntries(self):
        nr = 0
        for i in self.subDirs:
            if i.FileID != -1:
                nr += 1
            nr += i.getNrOfEntries()
        return nr

    def setOffset(self, offset):
        self.offset = offset
        return offset+self.FileSize

    def getLengthOfStrings(self):
        l = len(self.name) + 1
        for i in self.subDirs:
            if i.FileID != -1:
                l += i.getLengthOfStrings()
        return l

    def setFileSize(self, FileSize):
        self.FileSize = FileSize


RootDir = fstDir("", 1)


def calcSizeOfFST():
    size = RootDir.getNrOfEntries()*0xc+0xc
    size += RootDir.getLengthOfStrings()
    return size-1 # subtract emptyChar of RootDir

def addFileToFST(name, FileID, FileSize):
    curDir = RootDir
    name = name[1:]

    while name != "":
        pos = name.find("/")
        if pos != -1:
            curDir = curDir.addSubDir(name[0:pos])
            name = name[pos+1:]
        else:
            curDir.addFile(name, FileID, FileSize)
            name = ""
            
def setOffsetOfFile(name, offset):
    curDir = RootDir
    name = name[1:]

    while name != "":
        pos = name.find("/")
        if pos != -1:
            curDir = curDir.getSubDir(name[0:pos])
            name = name[pos+1:]
        else:
            #name = ""
            curDir = curDir.getSubDir(name)
            return curDir.setOffset(offset)
    return 0
            
def setFileSize(name, FileSize):
    curDir = RootDir
    name = name[1:]

    while name != "":
        pos = name.find("/")
        if pos != -1:
            curDir = curDir.getSubDir(name[0:pos])
            name = name[pos+1:]
        else:
            curDir = curDir.getSubDir(name)
            curDir.setFileSize(FileSize)
            return 1
    return 0
        


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

def getOutputRomMapFileID():
    output = ""
    
    RomMap.sort(key=operator.attrgetter('fileID'))
    for item in RomMap:
        output += hex(int(item.fileID)) + " " + str(item.name) + " "+ hex(item.address) + " " + hex(item.size) + "\n"
    
    return output

def alignFileSizeWithZeros(file, pos, alignment):
    target = (pos + alignment - 1) & (0x100000000-alignment)
    amount = target - pos
    file.write(b'\0' * amount)

def create_rom(dir, filename, fst_filename, fstmap, debug=False):
    with open(fstmap) as fin:
        for line in fin:
            words = line.split() # address, path+name, fileID, size
            if len(words) == 4:
                filepath = dir + words[1]
                FileSize = os.path.getsize(filepath)
                addRomSection(words[1], int(words[0], 16), FileSize, int(words[2], 16))
                addFileToFST(words[1], int(words[2], 16), FileSize)

    setFileSize("/fst.bin", alignAdr(calcSizeOfFST(), 4))
    offset = 0
    with open(fstmap) as fin:
        for line in fin:
            words = line.split() # address, path+name, fileID, size
            if len(words) == 4:
                offset = setOffsetOfFile(words[1], offset)
                if (words[1] == "/appldr.bin") or (words[1] == "/bootfile.dol"):
                    offset = alignAdr(offset, 0x100)
                offset = alignAdr(offset, 4)

    output = ""
    output += getOutputRomMapFileID() + "\n"
    output += RootDir.printDir("")
    #output += "\nFSTSize: " + hex(calcSizeOfFST())
    # (FST, string)
    newFST = RootDir.createFST(0, 0, 0)
    #output += "\nCreatedFST: " + str(newFST)

    # write new fst.bin-file
    if os.path.dirname(fst_filename) != "":
        if not os.path.exists(os.path.dirname(fst_filename)):
            os.makedirs(os.path.dirname(fst_filename))
    output_fst = open(fst_filename, 'wb')
    for i in newFST[0]:
        byte1 = i & 0xff
        byte2 = (i >> 8) & 0xff
        byte3 = (i >> 16) & 0xff
        byte4 = (i >> 24) & 0xff
        output_fst.write(struct.pack('BBBB', byte4, byte3, byte2, byte1))
    output_fst.write(bytearray(newFST[1], 'utf8'))
    output_fst.close()

    if os.path.dirname(filename) != "":
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
    output_rom = open(filename, 'wb')

    bootfile_offset = 0
    fst_offset = 0
    with open(fstmap) as fin:
        for line in fin:
            words = line.split() # address, path+name, fileID, size
            if len(words) == 4:
                filepath = dir + words[1]
                print("writing " + dir + words[1])
                filepart = bytearray(open(filepath, "rb").read())

                if (words[1] == "/bootfile.dol"):
                    bootfile_offset = output_rom.tell()
                    print("bootfile_offset: " + hex(bootfile_offset))
                elif (words[1] == "/fst.bin"):
                    fst_offset = output_rom.tell()
                    print("fst_offset: " + hex(fst_offset))

                output_rom.write(filepart)

                if (words[1] == "/appldr.bin") or (words[1] == "/bootfile.dol"):
                    alignFileSizeWithZeros(output_rom, output_rom.tell(), 0x100)
                else:
                    alignFileSizeWithZeros(output_rom, output_rom.tell(), 0x4)

    output_rom.seek(0x420)
    output_rom.write(struct.pack('>II', int(bootfile_offset), int(fst_offset)))

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-pack', action='store', nargs=4, type=str, metavar=("inputDir", "fstFile", "fstMap", "outputFile"), help="pack files into a gamecube iso")
    group.add_argument('-unpack', action='store', nargs=3, type=str, metavar=("inputFile", "outputDir", "outFilelist"), help="unpack files from a gamecube iso")
    args = parser.parse_args()

    debug = True

    output = ""
    if args.pack:
        output = create_rom(args.pack[0], args.pack[3], args.pack[1], args.pack[2], debug)
    if args.unpack:
        diagnose(args.unpack[0], args.unpack[1], args.unpack[2], debug)

    print(output)
