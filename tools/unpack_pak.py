# -*- coding: utf-8 -*-

import os
import sys
from filehandler import FileHandler

import configuration


class Win32Exe(object):
    def __init__(self, config):
        self.config = config

    def diagnose(self, filename="baserom.nds", filedir="", outFileList="", debug=False):
        rom = FileHandler()
        base_address = 0x0
        rom.init(filename, base_address)

        header_output = ""
        
        dol = BecFS()
        header_output += dol.diagnose(rom, base_address, filedir, debug)
        
        headerfilename = filedir + outFileList
        if not os.path.exists(os.path.dirname(headerfilename)) and os.path.dirname(headerfilename):
            os.makedirs(os.path.dirname(headerfilename))
        fheader = open(headerfilename, 'w')
        fheader.write(header_output)
        
        output = ""
        return (output)


class BecFS(object):
    def diagnose(self, file, base_address, filedir="", debug=False):
        output = ""
        
        NrOfFiles = file.ReadHWord_r(base_address+0x4)
        print "Nr of Files: " + hex(NrOfFiles)
        output += hex(NrOfFiles) + "\n"
        
        DataOffset = []
        DataSize = []
        DataMagic = []
        DataStringOffset = []
        for i in range(NrOfFiles):
            DataStringOffset += [file.ReadWord_r(base_address+0x8+0x10*i)]
            DataOffset += [file.ReadWord_r(base_address+0xc+0x10*i)]
            DataSize += [file.ReadWord_r(base_address+0x10+0x10*i)]
            DataMagic += [file.ReadWord_r(base_address+0x14+0x10*i)]
        
        filename = ""
        for i in range(NrOfFiles): # NrOfFiles
            filename = file.ReadString0(DataStringOffset[i], 0x20)
            file.WriteSectionInFile(filedir + filename, DataOffset[i], DataSize[i])
            print filename
            output += filename + " " + hex(DataOffset[i]) + " " + hex(DataSize[i]) + " " + hex(DataMagic[i]) + " " + hex(DataStringOffset[i]) + "\n"
        
        return output

        
if __name__ == "__main__":
    conf = configuration.Config()
    dvd = Win32Exe(conf)
    
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
