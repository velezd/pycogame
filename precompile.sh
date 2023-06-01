#!/bin/bash

print_help() {
    cat << EOF
precompile.sh [options] script
Compiles .py scripts into .mpy files, runs inside pycogame container

SCRIPT
    Path to micropython script, relative to code/ directory

OPTIONS
    -o  Optimisation level
        The optimisation level controls the following compilation features:
        - Assertions: at level 0 assertion statements are enabled and compiled 
          into the bytecode; at levels 1 and higher assertions are not compiled.
        - Built-in __debug__ variable: at level 0 this variable expands to True;
          at levels 1 and higher it expands to False.
        - Source-code line numbers: at levels 0, 1 and 2 source-code line number
          are stored along with the bytecode so that exceptions can report the 
          line number they occurred at; at levels 3 and higher line numbers are
          not stored.
        The default optimisation level is 3
    -h  Shows this help
EOF
}

SCRIPT=""
OPTIMIZATION=3
COMMAND="./micropython/mpy-cross/mpy-cross"

while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -o)
      OPTIMIZATION="$2"
      shift
      shift
      ;;
    -h)
      print_help
      exit 0
      shift
      ;;
    *)
      SCRIPT="$1"
      shift
      ;;
  esac
done

if [ -z "$SCRIPT" ]; then
    echo 'Missing path to script.'
    print_help
    exit 1
fi

if [ ! -x "$COMMAND" ]; then
    make setup
fi

podman run --rm -it \
-v ./code:/root/pycogame:Z \
-v ./micropython:/root/pycogame/micropython:Z \
-w /root/pycogame pycogame $COMMAND -O$OPTIMIZATION $SCRIPT