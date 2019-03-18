# -*- coding: utf-8 -*-

import os
import sys
from ctypes import c_int8
from util.io import BinaryIO

# https://docs.python.org/2/tutorial/inputoutput.html


class FileHandler(object):
    file = None
    base_address = 0
    filename = ""
    filesize = 0
    
    def __init__(self):
        return

    def init(self, filename, base_address):        
        self.filename = filename
        self.file = open(filename, "rb+")
        self.base_address = base_address
        self.filesize = self.GetFileSize()
        #print self.file.name

    def GetFileName(self):
        return self.filename

    def GetBaseAddress(self):
        return self.base_address

    def GetFileSize(self):
        self.file.seek(0, os.SEEK_END)
        return self.file.tell()

    def AdrInRange(self, adr, debug=False):
        if (adr < self.base_address) | (adr >= (self.base_address+self.filesize)):
            if debug:
                print("AdrInRange: " + hex(self.base_address) + " - " + hex(adr) + " - " + hex((self.base_address+self.filesize)))
            return False
        return True
    
    def ReadDWord(self, address):
        if not self.AdrInRange(address):
            return 0
        
        address = (address & 0xffffffff) - self.base_address
        self.file.seek(address)
        word = bytearray(self.file.read(8))
        return (word[0] << 56) | (word[1] << 48) | (word[2] << 40) | (word[3] << 32) | (word[4] << 24) | (word[5] << 16) | (word[6] << 8) | (word[7] << 0)
    
    def ReadWord(self, address):
        if not self.AdrInRange(address):
            return 0
        
        address = (address & 0xffffffff) - self.base_address
        self.file.seek(address)
        word = bytearray(self.file.read(4))
        return (word[0] << 24) | (word[1] << 16) | (word[2] << 8) | (word[3] << 0)
    
    def ReadWord_r(self, address):
        if not self.AdrInRange(address):
            return 0
        
        address = (address & 0xffffffff) - self.base_address
        self.file.seek(address)
        word = bytearray(self.file.read(4))
        return (word[3] << 24) | (word[2] << 16) | (word[1] << 8) | (word[0] << 0)

    def ReadHWord(self, address):
        if not self.AdrInRange(address):
            return 0
        
        address = (address & 0xffffffff) - self.base_address
        self.file.seek(address)
        hword = bytearray(self.file.read(2))
        return (hword[0] << 8) | (hword[1] << 0)

    def ReadHWord_r(self, address):
        if not self.AdrInRange(address):
            return 0
        
        address = (address & 0xffffffff) - self.base_address
        self.file.seek(address)
        hword = bytearray(self.file.read(2))
        return (hword[1] << 8) | (hword[0] << 0)

    def ReadByte(self, address):
        if not self.AdrInRange(address):
            return 0
        
        address = (address & 0xffffffff) - self.base_address
        self.file.seek(address)
        byte = bytearray(self.file.read(1))
        return (byte[0] << 0)

    def Read(self, address, size):
        if not self.AdrInRange(address):
            return 0
        
        address = (address & 0xffffffff) - self.base_address
        self.file.seek(address)
        return bytearray(self.file.read(size))

    def ReadString(self, address, size):
        if not self.AdrInRange(address):
            return 0
        
        address = (address & 0xffffffff) - self.base_address
        self.file.seek(address)
        string = ""
        for i in range(size):
            byte = bytearray(self.file.read(1))
            if(byte[0] != 0):
                string += chr(byte[0])
        return string

    def ReadString0(self, address, size):
        if not self.AdrInRange(address):
            return 0
        
        address = (address & 0xffffffff) - self.base_address
        self.file.seek(address)
        string = ""
        bytes = bytearray(self.file.read(size))
        for i in range(size):
            if(bytes[i] != 0):
                string += chr(bytes[i])
            else:
                break
                '''if((i+4) < size):
                    if((i%4) == 0):
                        return string #+ "\0\0\0\0"
                    if(((i%4) == 3) & (bytes[i+0] == 0)):
                        return string #+ "\0"
                    elif(((i%4) == 2) & (bytes[i+0] == 0) & (bytes[i+1] == 0)):
                        return string #+ "\0\0"
                    elif(((i%4) == 1) & (bytes[i+0] == 0) & (bytes[i+1] == 0) & (bytes[i+2] == 0)):
                        return string #+ "\0\0\0"
                return ""'''

        
        return string

    def ReadUnicodeString(self, address, size):
        if not self.AdrInRange(address):
            return 0
        
        address = (address & 0xffffffff) - self.base_address
        self.file.seek(address)
        string = ""
        for i in range(size):
            word = bytearray(self.file.read(2))
            if(word[0] != 0):
                string += unichr(word[0])
        return string

    def ReadHexString(self, address, size):
        if not self.AdrInRange(address):
            return 0
        
        address = (address & 0xffffffff) - self.base_address
        self.file.seek(address)
        string = ""
        for i in range(size):
            byte = bytearray(self.file.read(1))
            string += ("%02x" % byte[0]) # {:02x}'.format(byte[0])
        return string

    def WriteSectionInFile(self, filename, addr, size):
        #if size == 0: return None
        if os.path.isdir(filename): return None
        
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        
        print "Write section in file " + filename
        
        f = open(filename, 'wb')
        fByteArray = self.Read(addr, size)
        f.write(fByteArray)
        return None

    def write_array_in_file(self, array, infile):
        #if size == 0: return None
        if not os.path.exists(os.path.dirname(infile)):
            os.makedirs(os.path.dirname(infile))
        f = open(infile, 'wb')
        
        fByteArray = bytearray(array)
        f.write(fByteArray)
        f.close()
        return None
