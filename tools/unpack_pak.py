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
        
    print "Write section in file " + filename2 + " " + m.hexdigest()
	
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


class Win32Exe(object):
    def diagnose(self, filename="baserom.nds", filedir="", outFileList="", debug=False):
        file = open(filename, "rb+")

        header_output = ""
        
        dol = BecFS()
        header_output += dol.diagnose(file, filedir, debug)
        
        headerfilename = filedir + outFileList
        if not os.path.exists(os.path.dirname(headerfilename)) and os.path.dirname(headerfilename):
            os.makedirs(os.path.dirname(headerfilename))
        fheader = open(headerfilename, 'w')
        fheader.write(header_output)
        
        output = ""
        return (output)


class BecFS(object):
    def diagnose(self, file, filedir="", debug=False):
        output = ""
        
        file.seek(0x4)
        data = file.read(2)
        NrOfFiles, = struct.unpack("<H", data)
        print "Nr of Files: " + hex(NrOfFiles)
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
            print filename2
            output += filename2 + " " + hex(DataOffset[i]) + " " + hex(DataSize[i]) + " " + hex(DataMagic[i]) + " " + hex(DataStringOffset[i]) + "\n"
        
        return output

        
if __name__ == "__main__":
    dvd = Win32Exe()
    
    filename = ""
    outdir = ""
    output = ""
    outFileList = ""
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-x":
            cmd = "unpack"
            filename = sys.argv[i+1]
            outdir = os.path.splitext(filename)[0]
            i += 2
        elif sys.argv[i] == "-d":
            cmd = "diagnose"
            filename = sys.argv[i+1]
            outdir = os.path.dirname(filename)
            outFileList = "bec_info.txt"
            i += 2
        elif sys.argv[i] == "-of":
            outdir = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-filelist":
            outFileList = sys.argv[i+1]
            i += 2
    
    print(cmd + ': ' + filename)
    
    if cmd == "diagnose":
        print(cmd + ' to ' + outFileList)
        output = dvd.diagnose(filename, outdir, outFileList)
    
    print output
