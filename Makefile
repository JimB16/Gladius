
PYTHON := python
MKDIR_P = mkdir -p

.PHONY: all init

unpack_iso     := $(PYTHON) tools/unpack_iso.py
unpack_bec     := $(PYTHON) tools/unpack_bec.py
create_iso     := $(PYTHON) tools/create_iso.py
create_bec     := $(PYTHON) tools/create_bec.py

all:

clean:
	rm -f build/*
	rm gladius.iso

init:
	$(unpack_iso) -d "./baseiso.iso" -of "./baseiso/" -filelist "BaseISO_FileList.txt" -export
	$(unpack_bec) -d "./baseiso/gladius.bec" -of "./baseiso/gladius_bec/" -filelist "gladius_bec_FileList.txt"

build/gladius.bec:
	$(MKDIR_P) build/
	$(create_bec) -dir "./baseiso/gladius_bec" -becmap "./baseiso/gladius_bec/gladius_bec_FileList.txt" -o $@

gladius.iso: build/gladius.bec
	$(MKDIR_P) build/
	$(create_iso) -dir "./baseiso" -fst "./baseiso/fst.bin" -fstmap "./baseiso/BaseISO_FileList.txt" -o $@
	md5sum $@

gladius: gladius.iso
