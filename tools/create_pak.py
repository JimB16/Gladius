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
    def __init__(self, name, name2, hash, address, size2, flags, size, checksum):
        self.name = name
        self.name2 = name2
        self.hash = hash
        self.address = address
        self.new_address = address
        self.flags = flags
        self.size = size
        self.size2 = size2
        self.new_size = size
        self.checksum = checksum

def getAddress(item):
    return item.address

RomMap = []

def addRomSection(name, name2, hash, address, size2, flags, size, checksum): # filename, hash?, offset, offsetcorrection, flags?, filesize, checksum?
    #if size > 0:
    RomMap.append(RomSection(name, name2, hash, address, size2, flags, size, checksum))
    return None

def changeAddressOfRomSection(old_addr, new_addr, old_size, new_size):
    for item in RomMap:
        if ((item.flags != 0) and (item.address == old_addr) and (item.size == old_size)):
            item.address = new_addr
            item.size = new_size

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

    def create_rom(self, dir, filename, fst_filename, becmap, debug=False):
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
                    filepath = os.path.join(self.config.path, dir + "/" + words[0])
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
        output_rom.write(struct.pack('<4s', "PAK1"))
        output_rom.write(struct.pack('<I', int(NrOfFiles)))
    
        for i in range(NrOfFiles):
            output_rom.write(struct.pack('<I', int(filenameoffsets[i])))
            output_rom.write(struct.pack('<I', int(fileoffsets[i])))
            output_rom.write(struct.pack('<I', int(filesizes[i])))
            output_rom.write(struct.pack('<I', int(FileMagic[i])))
    
		# write filename strings
        for i in range(NrOfFiles):
            output_rom.write(os.path.basename(filepaths[i]))
            output_rom.write(struct.pack('<B', int(0)))
    
        while((output_rom.tell() % 0x4) != 0):
            output_rom.write(struct.pack('<B', int(0xaf)))
    
		# write file data into package
        for i in range(NrOfFiles):
            filepart = bytearray(open(filepaths[i], "rb").read())
            output_rom.write(filepart)
            while((output_rom.tell() % 0x4) != 0):
                output_rom.write(struct.pack('<B', int(0xaf)))
        '''RomMap.sort(key=operator.attrgetter('address')) # address
        i = 0
        for item in RomMap:
            if item.flags != 0:
                print "not writing " + dir + "/" + item.name + " with flag " + hex(item.flags)
                continue
            if item.size2 != 0:
                filepath2 = os.path.join(self.config.path, dir + "/" + item.name2)
                filepart2 = bytearray(open(filepath2, "rb").read())
                output_rom.write(filepart2)
                output_rom.write(struct.pack('<I', int(0))) # checksum? PS2Exclusive
                output_rom.write(struct.pack('<I', int(0))) # PS2Exclusive
                while((output_rom.tell() % filealignment) != 0):
                    output_rom.write(struct.pack('<B', int(0)))
            filepath = os.path.join(self.config.path, dir + "/" + item.name)
            filepart = bytearray(open(filepath, "rb").read())
            output_rom.write(filepart)
            while((output_rom.tell() % filealignment) != 0):
                output_rom.write(struct.pack('<B', int(0)))
            if (item.size2 == 0) and (item.size == 0):
                output_rom.write('\0' * (filealignment)) # write dvd filler material into archive
            i += 1'''
        
        return output


if __name__ == "__main__":
    conf = configuration.Config()
    disasm = Disassembler(conf)

    filename = ''
    becmap = ''
    fst_file = '' # removed
    dir = ''
    debugFlag = False
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-dir":
            dir = sys.argv[i+1]
            i += 2
        if sys.argv[i] == "-becmap":
            becmap = sys.argv[i+1]
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

    output = disasm.create_rom(dir, filename, fst_file, becmap)
    print output
