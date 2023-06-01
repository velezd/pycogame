#!/usr/bin/python
""" Utility to convert images to raw RGB565 format """

from PIL import Image
from skimage import exposure, io
from struct import pack
from os import path, mkdir
import sys


def error(msg):
    """ Display error and exit """
    print (msg)
    sys.exit(-1)


def write_bin(f, pixel_list):
    """ Save image in RGB565 format """
    for pix in pixel_list:
        r = (pix[0] >> 3) & 0x1F
        g = (pix[1] >> 2) & 0x3F
        b = (pix[2] >> 3) & 0x1F
        f.write(pack('>H', (r << 11) + (g << 5) + b))


def adjust_gamma(in_path, num):
    """ Creates copy of image with adjusted gamma

    :param in_path: Path to image file
    :type in_path: str
    :param num: Gamma correction
    :type num: float
    :return: Path to modified file
    :rtype: str
    """
    modified_dir = path.join(path.dirname(path.abspath(in_path)), 'gamma_corrected')
    if not path.isdir(modified_dir):
        mkdir(modified_dir)

    filename, ext = path.splitext(path.basename(in_path))
    img = io.imread(in_path)
    gamma_corrected = exposure.adjust_gamma(img, num)
    new = path.join(modified_dir, filename + '.png')
    io.imsave(new, gamma_corrected)

    return new

if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        error('Please specify input file: ./img2rgb565.py test.png')

    new_dir = path.join(path.dirname(path.abspath(args[1])), 'converted')
    if not path.isdir(new_dir):
        mkdir(new_dir)
    
    for in_path in args[1:]:

        if not path.exists(in_path):
            error('File Not Found: ' + in_path)

        in_path = adjust_gamma(in_path, 1.5)
        filename, ext = path.splitext(in_path)
        filename = path.basename(filename)

        out_path = path.join(new_dir, filename + '.raw')
        img = Image.open(in_path)
        pixels = list(img.getdata().convert('RGB'))

        with open(out_path, 'wb') as f:
            write_bin(f, pixels)

        print('Saved: ' + out_path)
