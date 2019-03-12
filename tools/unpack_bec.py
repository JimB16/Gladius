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
        #header_output += rom.GetFileName() + "\n"
        #header_output += "FileSize:    " + hex(rom.GetFileSize()) + "\n"
        
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
        
        NrOfFiles = file.ReadWord_r(base_address+0x8)
        print "Nr of Files: " + hex(NrOfFiles)
        
        DataPos = []
        DataOffset = []
        Data3 = []
        DataSize = []
        for i in range(NrOfFiles):
            DataPos += [file.ReadWord_r(base_address+0x10+0x10*i)]
            DataOffset += [file.ReadWord_r(base_address+0x14+0x10*i)]
            Data3 += [file.ReadWord_r(base_address+0x18+0x10*i)] # 0 or 2
            DataSize += [file.ReadWord_r(base_address+0x1c+0x10*i)]
        
        filename = ""
        #print "DataOffset[0]: " + hex(DataOffset[0])
        for i in range(NrOfFiles): # NrOfFiles
            if file.ReadHWord(DataOffset[i]) == 0x2f2f:
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x0D0A2F2F):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x0D0A0D0A) and (file.ReadHWord(DataOffset[i]+4) == 0x2F2F):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x436F7079) and (file.ReadWord(DataOffset[i]+4) == 0x72696768):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x56455253):
                filename = str(i) + ".vers"
            elif (file.ReadWord(DataOffset[i]) == 0x50545450):
                filename = str(i) + ".pttp"
            elif (file.ReadWord(DataOffset[i]) == 0x50414B31):
                filename = str(i) + ".pak1"
            elif (file.ReadWord(DataOffset[i]) == 0x23233832) and (file.ReadWord(DataOffset[i]+4) == 0x32300D0A):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x1D200000):
                filename = str(i) + ".bin"
            elif (file.ReadWord(DataOffset[i]) == 0x504D5332):
                filename = str(i) + ".pms2"
            elif (file.ReadWord(DataOffset[i]) == 0x40656368) and (file.ReadWord(DataOffset[i]+4) == 0x6F206F66):
                filename = str(i) + ".bat"
            elif (file.ReadWord(DataOffset[i]) == 0x504F5309):
                filename = str(i) + ".pos"
            elif (file.ReadWord(DataOffset[i]) == 0x0D0A6675):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x4C4F4341) and (file.ReadWord(DataOffset[i]+4) == 0x544F5253):
                filename = str(i) + ".locators"
            elif (file.ReadWord(DataOffset[i]) == 0x312C2242) and (file.ReadWord(DataOffset[i]+4) == 0x6174746C):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x66756E63) and (file.ReadWord(DataOffset[i]+4) == 0x74696F6E):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x52454D20) and (file.ReadWord(DataOffset[i]+4) == 0x2D2D2047):
                filename = str(i) + ".bat"
            elif (file.ReadWord(DataOffset[i]) == 0x53554254) and (file.ReadWord(DataOffset[i]+4) == 0x49544C45):
                filename = str(i) + ".subs.txt"
            elif (file.ReadWord(DataOffset[i]) == 0x53474F44):
                filename = str(i) + ".sgod"
            elif (file.ReadWord(DataOffset[i]) == 0x0D0A0D0A):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x4E554D45) and (file.ReadWord(DataOffset[i]+4) == 0x44474553):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x4E554D43) and (file.ReadWord(DataOffset[i]+4) == 0x52454449):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x01000000):
                filename = str(i) + ".bin"
            elif (file.ReadWord(DataOffset[i]) == 0x02000000):
                filename = str(i) + ".bin"
            elif (file.ReadWord(DataOffset[i]) == 0x4E414D45):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x200D0A2F):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x50415448):
                filename = str(i) + ".bat"
            elif (file.ReadWord(DataOffset[i]) == 0x0D0A4E41):
                filename = str(i) + ".txt"
            elif (file.ReadHWord(DataOffset[i]) == 0x2E2E) and (file.ReadByte(DataOffset[i]+2) == 0x5C):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x54494E54) and (file.ReadWord(DataOffset[i]+4) == 0x494E473A):
                filename = str(i) + ".tinting.txt"
            elif (file.ReadWord(DataOffset[i]) == 0x0D0A2066):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x4D4F4449) and (file.ReadWord(DataOffset[i]+4) == 0x54454D53):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x5343454E) and (file.ReadWord(DataOffset[i]+4) == 0x453A0909):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x496E7465) and (file.ReadWord(DataOffset[i]+4) == 0x72666163):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x4C656167) and (file.ReadWord(DataOffset[i]+4) == 0x75655374):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x5C70726F) and (file.ReadWord(DataOffset[i]+4) == 0x6A656374):
                filename = str(i) + ".txt"
            elif (file.ReadHWord(DataOffset[i]) == 0x0D0A):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x5041583A):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x3A204765):
                filename = str(i) + ".bat"
            elif (file.ReadWord(DataOffset[i]) == 0x6275696C) and (file.ReadWord(DataOffset[i]+4) == 0x6470616B):
                filename = str(i) + ".txt"
            elif (file.ReadWord(DataOffset[i]) == 0x5363686F) and (file.ReadWord(DataOffset[i]+4) == 0x6F6C5374):
                filename = str(i) + ".txt"
            else:
                filename = str(i) + ".bin"
            file.WriteSectionInFile(filedir + filename, DataOffset[i], DataSize[i])
            output += filename + " " + hex(DataPos[i]) + " " + hex(DataOffset[i]) + " " + hex(Data3[i]) + " " + hex(DataSize[i]) + "\n"
        
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
