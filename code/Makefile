.PHONY: all setup firmware

all: setup firmware

setup:
	make -C micropython/mpy-cross

firmware:
	cp -f pycogame.py ./micropython/ports/rp2/modules/
	cp -f pglauncher.py ./micropython/ports/rp2/modules/
	cp -f ./micropython/drivers/sdcard/sdcard.py ./micropython/ports/rp2/modules/
	make -C micropython/ports/rp2
