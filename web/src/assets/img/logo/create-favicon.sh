#!/bin/bash -e

inkscape -w 16 -h 16 -e 16.png logo-black.min.svg
inkscape -w 32 -h 32 -e 32.png logo-black.min.svg
inkscape -w 48 -h 48 -e 48.png logo-black.min.svg

convert 16.png 32.png 48.png favicon.ico

rm 16.png 32.png 48.png
