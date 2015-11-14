#encoding=utf-8

import struct
from math import ceil
import StringIO
import numpy as np
import random

FORMAT_OFFSET = int('0',16)
SIZE_OFFSET = int('2',16)
DATA_OFFSET = int('0a', 16)
BISIZE_OFFSET = int('0e', 16)
WIDTH_OFFSET = int('12',16)
HEIGHT_OFFSET = int('16',16)
BPP_OFFSET = int('1c',16)
BIX = int('26', 16)
BICLR = int('2e', 16)
HORIZONTAL = 0
VERTICAL = 1

class readImg:
    def __init__(self, filename):
        '''Main class to open and edit a 24 bits bmp image'''

        bmpfile = open(filename)
        self.raw_data = bmpfile.read()
        bmpfile.close()

        self.width = struct.unpack_from("<i", self.raw_data, WIDTH_OFFSET)[0]
        self.height = struct.unpack_from("<i", self.raw_data, HEIGHT_OFFSET)[0]
        self.data_offset = ord(self.raw_data[DATA_OFFSET])
        self.bpp = ord(self.raw_data[BPP_OFFSET])  # Bits Per Pixel
        self.bitmap = []

        if self.raw_data[0] != "B" and self.raw_data[1] != "M":
            raise TypeError, "Not a BMP file!"
        if self.bpp != 24:
            raise TypeError, "Not a 24 bits BMP file"

        # 11.12 added
        self.create_bitmap()



    def create_bitmap(self):
        '''Creates the bitmap from the raw_data'''

        off = self.data_offset
        width_bytes = self.width*(self.bpp/8)
        rowstride = ceil(width_bytes/4.0)*4
        padding = int(rowstride - width_bytes)

        for y in xrange(self.height):
            self.bitmap.append([])

            for x in xrange(self.width):
                b = ord(self.raw_data[off])
                g = ord(self.raw_data[off+1])
                r = ord(self.raw_data[off+2])

                off = off+3

                self.bitmap[y].append([r, g, b])

            off += padding

        self.bitmap = self.bitmap[::-1]
        ## 11.12 deleted
        ## return self.bitmap

    def save_to(self, filename):
        '''Export the bmp saving the changes done to the bitmap'''
        raw_copy = StringIO.StringIO()
        bitmap = self.bitmap[::-1]

        width_bytes = self.width*(self.bpp/8)
        rowstride = ceil(width_bytes/4.0)*4
        padding = int(rowstride - width_bytes)

        # Same header as before until the width
        raw_copy.write(self.raw_data[:WIDTH_OFFSET])

        s = struct.Struct("<i")
        _w = s.pack(self.width)   # Transform width, height to
        _h = s.pack(self.height)  # little indian format
        raw_copy.write(_w)
        raw_copy.write(_h)

        # After the new width and height the header it's the same
        raw_copy.write(self.raw_data[HEIGHT_OFFSET+4:self.data_offset])

        for y in xrange(self.height):
            for x in xrange(self.width):
                r, g, b = bitmap[y][x]

                # Out of range control
                if r > 255: r = 255
                if g > 255: g = 255
                if b > 255: b = 255
                if r < 0: r = 0
                if g < 0: g = 0
                if b < 0: b = 0

                #Char transformation
                r = chr(r)
                g = chr(g)
                b = chr(b)

                raw_copy.write(b + g + r)

            raw_copy.write(chr(0)*padding)

        self.raw_data = raw_copy.getvalue()

        f = open(filename, "w")
        f.write(self.raw_data)
        f.close()
        f.close()

    def rgb2gray(self):
        for y in range(self.height):
            for x in range(self.width):
                try:
                    mean = sum(self.bitmap[y][x])/3
                    colour = (mean, mean, mean)
                    self.bitmap[y][x] = colour
                except IndexError as e:
                    continue

    def mirror(self, direction = HORIZONTAL):
        if direction == HORIZONTAL:
            for y in xrange(self.height):
                self.bitmap[y] = self.bitmap[y][::-1]
        elif direction == VERTICAL:
            self.bitmap= self.bitmap[::-1]

    def move(self, dx, dy):

        if dx > 0:
            for i in range(self.height):
                for j in range(1, self.width-dx):
                    self.bitmap[i][-j] = self.bitmap[i][-j-dx]
            for i in range(self.height):
                for j in range(dx):
                    self.bitmap[i][j] = (0, 0, 0)
        else:
            for i in range(self.height):
                for j in range(self.width+dx):
                    self.bitmap[i][j] = self.bitmap[i][j-dx]
            for i in range(self.height):
                for j in range(-1,dx,-1):
                    self.bitmap[i][j] = (0,0,0)
        if dy > 0:
            for i in range(1, self.height-dy):
                for j in range(self.width):
                    self.bitmap[-i][j] = self.bitmap[-i-dy][j]
            for i in range(dy):
                for j in range(self.width):
                    self.bitmap[i][j] = (0, 0, 0)
        else:
            for i in range(self.height+dy):
                for j in range(self.width):
                    self.bitmap[i][j] = self.bitmap[i-dy][j]
            for i in range(-1, dy, -1):
                for j in range(self.width):
                    self.bitmap[i][j] = (0,0,0)


    # 11.12added
    def getPix(self, point):
        return self.bitmap[point[1]][point[0]]




if __name__ == '__main__':
    img =readImg('../bear1107.bmp')
    img.move(20,30)
    img.save_to('./tmp.bmp')
    #img.save_to(filename="../bear1107.bmp", data = bitmap)



