.PHONY: all setup build clean

all: setup build

setup:
	git submodule update --init
	git -C micropython submodule update --init -- lib/pico-sdk lib/tinyusb
	podman build . --tag pycogame
	podman run --rm -it \
	-v ./code:/root/pycogame:Z \
	-v ./micropython:/root/pycogame/micropython:Z \
	-w /root/pycogame pycogame make setup

build:
	podman run --rm -it \
	-v ./code:/root/pycogame:Z \
	-v ./micropython:/root/pycogame/micropython:Z \
	-w /root/pycogame pycogame make firmware

clean:
	podman image rm localhost/pycogame
