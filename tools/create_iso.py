# -*- coding: utf-8 -*-

import os
import sys
import struct
import operator
from copy import copy, deepcopy
from ctypes import c_int8

import configuration

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
        """
        if self.getFile(name) == None:
            self.Files.append(name)
        self.Files = sorted(self.Files)
        return self.getSubDir(name)
        """
    def printDir(self, offset):
        string = offset + self.name + " " + hex(self.getNrOfEntries()) + " " + hex(self.FileID) + " " + hex(self.offset) + "\n"
        for i in self.subDirs:
            #string += offset + i.name + "\n"
            string += i.printDir(offset + self.name + "/")
        for i in self.Files:
            string += offset + self.name + "/" + i + "\n"
        return string
    def createFST(self, string_table_length, parentID, ownID):
        # self.subDirs = sorted(self.subDirs, key=lambda fstDir: fstDir.offset)
        
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

def getAddress(item):
    return item.address

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

def getOutputRomMap():
    output = ""
    old_address = 0
    
    RomMap.sort(key=operator.attrgetter('address'))
    for item in RomMap:
        if old_address != item.address:
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


def words(fileobj):
    for line in fileobj:
        for word in line.split():
            yield word

class Disassembler(object):
    def __init__(self, config):
        self.config = config

    def fill_rom(self, filepath, file, align, filler):
        #statinfo = int(os.path.getsize(filepath))
        statinfo = file.tell()
        rest = statinfo % align
        if rest != 0: rest = align - rest
        i = 0
        
        while i < rest:
            file.write(filler)
            i += 1
        
        print "fill rom " + filepath + ": @" + hex(file.tell()) + " for " + hex(rest)
        return None

    def create_rom(self, dir, filename, fst_filename, fstmap, debug=False):
        with open(fstmap) as fin:
            for line in fin:
                words = line.split() # address, path+name, fileID, size
                if len(words) == 4:
                    filepath = os.path.join(self.config.path, dir + words[1])
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
        #output += str(RootDir.subDirs) + "\n"
        output += RootDir.printDir("")
        output += "\nFSTSize: " + hex(calcSizeOfFST())
        # (FST, string)
        newFST = RootDir.createFST(0, 0, 0)
        output += "\CreatedFST: " + str(newFST)

        
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
            output_fst.write(struct.pack('B', byte4))
            output_fst.write(struct.pack('B', byte3))
            output_fst.write(struct.pack('B', byte2))
            output_fst.write(struct.pack('B', byte1))
        output_fst.write(newFST[1])
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
                    filepath = os.path.join(self.config.path, dir + words[1])
                    print "writing " + dir + words[1]
                    filepart = bytearray(open(filepath, "rb").read())
                    
                    if (words[1] == "/bootfile.dol"):
                        bootfile_offset = output_rom.tell()
                        print("bootfile_offset: " + hex(bootfile_offset))
                    elif (words[1] == "/fst.bin"):
                        fst_offset = output_rom.tell()
                        print("fst_offset: " + hex(fst_offset))

                    output_rom.write(filepart)
                    
                    if (words[1] == "/appldr.bin") or (words[1] == "/bootfile.dol"):
                        disasm.fill_rom(filename, output_rom, 0x100, '\x00')
                    else:
                        disasm.fill_rom(filename, output_rom, 0x4, '\x00')
                        
        output_rom.seek(0x420, 0)
        output_rom.write(struct.pack('>I', int(bootfile_offset)))
        output_rom.seek(0x424, 0)
        output_rom.write(struct.pack('>I', int(fst_offset)))
        
        return output


if __name__ == "__main__":
    conf = configuration.Config()
    disasm = Disassembler(conf)

    filename = ''
    fstmap = ''
    fst_file = ''
    dir = ''
    debugFlag = False
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-dir":
            dir = sys.argv[i+1]
            i += 2
        if sys.argv[i] == "-fst":
            fst_file = sys.argv[i+1]
            i += 2
        if sys.argv[i] == "-fstmap":
            fstmap = sys.argv[i+1]
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

    output = disasm.create_rom(dir, filename, fst_file, fstmap)
    print output
