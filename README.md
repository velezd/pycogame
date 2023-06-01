# pycoGame

pycoGame is a handheld game console based on Raspberry Pi Pico and a MicroPython library for easy game development inspired by pygame.

More information at http://zveleba.cz/pages/blog/posts/pycogame.html

## Content
- Open hardware game console
- MicroPython library pycogame
- Game launcher
- Example games
    - FlappyTux (Flappy Bird clone)
    - Micronoid (Arkanoid clone)
    - MicroMaze 3D (Raycaster maze game)
- Game development tools
    - precompile
    - img2rgb565

## Download

Version 1.0

## Installation

- Program firmware onto RPi Pico
    ./micropython/ports/rp2/build-PICO/firmware.uf2
- Copy game launcher files to RPi Pico flash.
  Easiest tool for that is Thonny IDE, also useful for debugging.
- Copy games to SD Card

## Build firmware

- Get submodules and build container

    `make setup`

- Build

    `make build`

- Cleanup (optional)

    `make cleanup`

## Pre-compile MicroPython scripts

MicroPython scripts can be pre-compiled for 
faster execution and reduced memory usage.

This will run the build container and execute `make setup` if needed.

`./precompile.sh games/Test/game.py`

## Convering images to RGB565 format

Requires python libraries `scikit-image` and `PIL` (on fedora: `sudo dnf install python3-scikit-image python3-pillow`).
Multiple images can be converted at once.
The script contains workaround for inaccurate colors on the LCD (gamma correction).

Convered images are stored in directory `converted` 
and gamma corrected images are kept in directory
`gamma_corrected`, so you can use them to sample the
final color value.

`./img2rgb565.py img1.png img2.png ...`
