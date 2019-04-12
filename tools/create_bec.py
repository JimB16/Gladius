# -*- coding: utf-8 -*-

import os
import sys
import struct
import operator


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

RomMap = []

def addRomSection(name, name2, hash, address, size2, flags, size, checksum, checksum2): # filename, hash?, offset, offsetcorrection, flags?, filesize, checksum?
    RomMap.append(RomSection(name, name2, hash, address, size2, flags, size, checksum, checksum2))

def alignFileSizeWithZeros(file, pos, alignment):
    target = (pos + alignment - 1) & (0x100000000-alignment)
    amount = target - pos
    file.write('\0' * amount)


def createBecArchive(dir, filename, becmap, gc, debug=False):
    output = ""
    filealignment = 0x0
    NrOfFiles = 0x0
    HeaderMagic = 0x0
	
    with open(becmap) as fin:
        for line in fin:
            words = line.split() # filename, ?, offset, flags?, filesize
            if len(words) == 9:
                FileSize = os.path.getsize(dir + "/" + words[0])
                FileSize2 = 0
                if words[1] != "nothing":
                    FileSize2 = os.path.getsize(dir + "/" + words[1])
                addRomSection(words[0], words[1], int(words[2], 16), int(words[3], 16), FileSize2, int(words[5], 16), FileSize, int(words[7], 16), int(words[8], 16)) # filename, filename2, hash?, offset, filesize2, flags?, filesize, checksum?, checksum2?
            elif len(words) == 3:
                filealignment = int(words[0], 16)
                NrOfFiles = int(words[1], 16)
                HeaderMagic = int(words[2], 16)
        
    if os.path.dirname(filename) != "":
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
    output_rom = open(filename, 'wb')
	# write header
    output_rom.write(struct.pack('<4s', " ceb"))
    output_rom.write(struct.pack('<H', int(0x3)))
    output_rom.write(struct.pack('<H', int(filealignment)))
    output_rom.write(struct.pack('<I', int(NrOfFiles))) # Nr of files
    output_rom.write(struct.pack('<I', int(HeaderMagic)))
    
    # updated the filesizes
    RomMap.sort(key=operator.attrgetter('address')) # address
    addr = RomMap[0].address
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
        output_rom.write(struct.pack('<I', int(item.hash)))
        output_rom.write(struct.pack('<I', int(item.new_address)))
        output_rom.write(struct.pack('<B', int((item.size2 >> 0) & 0xff)))
        output_rom.write(struct.pack('<B', int((item.size2 >> 8) & 0xff)))
        output_rom.write(struct.pack('<B', int((item.size2 >> 16) & 0xff)))
        output_rom.write(struct.pack('<B', int(item.flags)))
        output_rom.write(struct.pack('<I', int(item.size)))

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
        #print("writing " + dir + "/" + item.name)
        filedata = bytearray(open(filepath, "rb").read())
        output_rom.write(filedata)
        if ((item.size2 == 0) and (item.size > 0)) or (gc == 1):
            output_rom.write(struct.pack('<II', item.checksum, item.checksum2)) # checksum? GCExclusive
		
        alignFileSizeWithZeros(output_rom, output_rom.tell(), filealignment)
			
        if (item.size2 == 0) and (item.size == 0) and (gc == 0):
            output_rom.write('\0' * (filealignment)) # write dvd filler material into archive PS2Exclusive
        
        i += 1
        if (i % 2500) == 0:
            print("write progress... " + str(i) + "/" + str(len(RomMap)))
        
    return output


if __name__ == "__main__":
    filename = ''
    becmap = ''
    dir = ''
    debugFlag = False
    gc = 0
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-gc": # switch between PS2 and GC Mode, the bec-formats they use don't seem completely compatible
            gc = 1
            i += 1
        elif sys.argv[i] == "-dir":
            dir = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-becmap":
            becmap = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-o":
            filename = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "-debug":
            debugFlag = True
            i += 2
        else:
            i += 1

    output = createBecArchive(dir, filename, becmap, gc, debugFlag)
	
    print(output)
