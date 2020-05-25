import struct
from dataclasses import dataclass
import re
from struct import unpack
from struct import pack
import copy

BMPHeader = 0x4D42


@dataclass
class BitMapFileHeader:
    size = None
    offset = None

    def __init__(self, size, offset):
        self.type = BMPHeader
        self.size = size
        self.offset = offset
        self.version = ''


class BitMapInfoHeader:
    color_important = None
    color_used = None
    compression = None
    planes = None
    size = None
    bit_count = None
    image_size = None
    width = None
    height = None

    def __init__(self):
        self.size = 40
        self.width = 0
        self.height = 0
        self.planes = 1
        self.bit_count = 0
        self.compression = 0
        self.image_size = 0
        self.color_used = 0
        self.color_important = 0



def open_file(filename):
    with open(filename, 'rb') as file:
        return file.read()


def check_if_file_is_bmp(file, name):
    if file[:2] != b'\x42\x4d':
        raise TypeError(name + " is not a BMP file")


def read_file_header(file):
    size = unpack('<I', file[0x2:0x6])[0]
    offset = unpack('<I', file[0xa:0xa + 4])[0]
    #version_size = unpack('<I', file[0xe:0xe + 4])[0]
    #version = VERSIONS.get(version_size, 'Invalid')
    return BitMapFileHeader(size, offset)


def fill_core_info(file):
    info = BitMapInfoHeader()
    info.width = unpack('<I', file[0x12:0x12 + 4])[0]
    info.height = unpack('<I', file[0x16:0x16 + 4])[0]
    info.planes = unpack('<H', file[0x1a:0x1a + 2])[0]
    info.bit_count = unpack('<H', file[0x1c:0x1c + 2])[0]
    info.image_size = info.width*info.height*info.bit_count//8
    return info


@dataclass
class RGB:
    red = None
    blue = None
    green = None

    def __init__(self):
        self.red = 0
        self.green = 0
        self.blue = 0


@dataclass
class RGBQuad:
    def __init__(self):
        self.red = 0
        self.green = 0
        self.blue = 0
        self.reserved = 0


class Image:
    def __init__(self):
        self.file = None
        self.rgb = None
        self.rgb_quad = None
        self.bitmap_info_header = BitMapInfoHeader
        self.bitmap_file_header = BitMapFileHeader

    def read_info_from_file(self, filename):
        self.file = open_file(filename)
        check_if_file_is_bmp(self.file, filename)
        self.bitmap_file_header = read_file_header(self.file)
        self.bitmap_info_header = fill_core_info(self.file)

    def write_image(self, filename: str):
        file = None
        while file is None:
            try:
                file = open(filename, "wb")
            except PermissionError:
                extension = filename[filename.rfind("."):len(filename)]
                filename[filename.rfind("."):len(filename)] = ""
                filename += "(1)" + extension

        if not self.bitmap_file_header.size == self.bitmap_file_header.offset + self.bitmap_info_header.image_size:
            self.bitmap_file_header.offset = 14 + self.bitmap_info_header.size
            if self.bitmap_info_header.bit_count == 24:
                self.bitmap_info_header.image_size += self.bitmap_info_header.width*3 - 2
            self.bitmap_file_header.size = self.bitmap_file_header.offset + self.bitmap_info_header.image_size

        info = self.bitmap_info_header
        fheader = self.bitmap_file_header
        file.write(pack("<HIII", BMPHeader, fheader.size+2, 0, fheader.offset))
        file.write(pack("<III", info.size, info.width, info.height))
        file.write(pack("<HHII", info.planes, info.bit_count, info.compression, info.image_size))
        file.write(pack("<II", 2834, 2834))
        file.write(pack("<II", info.color_used, info.color_important))
        if self.bitmap_info_header.bit_count == 24:
            for i in range(self.bitmap_info_header.height, -1, -1):
                for j in range(self.bitmap_info_header.width):
                    # print("{0} {1}".format(i,j))
                    file.write(pack("<B", self.rgb[i][j].blue))
                    file.write(pack("<B", self.rgb[i][j].green))
                    file.write(pack("<B", self.rgb[i][j].red))
        elif self.bitmap_info_header.bit_count == 32:
            for i in range(self.bitmap_info_header.height-1, -1, -1):
                for j in range(self.bitmap_info_header.width):
                    # print("{0} {1}".format(i,j))
                    file.write(pack("<B", self.rgb[i][j].blue))
                    file.write(pack("<B", self.rgb[i][j].green))
                    file.write(pack("<B", self.rgb[i][j].red))
                    file.write(pack("<B", 0))
        file.write(pack("<H", 0))

    @classmethod
    def read_from_file(cls, filename):
        img = Image()
        img.read_info_from_file(filename)
        img.read_pixels_from_file(img.file)
        return img

    def set_default_pixels(self, mode):
        self.rgb = [[RGB()] for i in range(self.bitmap_info_header.height+1)]
        for i in range(self.bitmap_info_header.height+1):
            self.rgb[i] = [RGB() for j in range(self.bitmap_info_header.width)]

        if type(mode) is not int or mode > 255 or mode < 0:
            mode = 255

        for i in range(self.bitmap_info_header.height+1):
            for j in range(self.bitmap_info_header.width):
                # print("{0} {1}".format(i,j))
                self.rgb[i][j].blue = 255
                self.rgb[i][j].green = 255
                self.rgb[i][j].red = 255

    def set_default_header(self, width = 800, height = 600, bit_count = 24):
        self.bitmap_info_header.width = width
        self.bitmap_info_header.height = height
        self.bitmap_info_header.bit_count = bit_count
        self.bitmap_info_header.image_size = 800*600*(bit_count//8) # change for less bits
        self.bitmap_info_header.size = 40
        self.bitmap_info_header.planes = 1
        self.bitmap_info_header.compression = 0
        self.bitmap_info_header.color_used = 0
        self.bitmap_info_header.color_important = 0

    @classmethod
    def set_default(cls, mode=255, width=800, height=600, bit_count=24):
        img = Image()
        img.set_default_header(width, height, bit_count)
        img.set_default_pixels(mode)
        return img

    def copy_info_header(self):
        header = BitMapInfoHeader()
        header.size = self.bitmap_info_header.size
        header.width = self.bitmap_info_header.width
        header.height = self.bitmap_info_header.height
        header.bit_count = self.bitmap_info_header.bit_count
        header.image_size = self.bitmap_info_header.image_size
        header.compression = self.bitmap_info_header.compression
        header.color_important = self.bitmap_info_header.color_important
        header.color_used = self.bitmap_info_header.color_used
        header.planes = self.bitmap_info_header.planes
        return header

    def __copy__(self):
        img = Image()
        img.bitmap_info_header = self.copy_info_header()
        img.bitmap_file_header = BitMapFileHeader(self.bitmap_file_header.size, self.bitmap_file_header.offset)
        if self.rgb is not None:
            img.rgb = copy.copy(self.rgb)
        else:
            img.rgb_quad = copy.copy(self.rgb_quad)
        return img

    def copy_with_changed_size(self, width:int, height:int):
        img = Image()
        img.bitmap_info_header = self.copy_info_header()
        img.bitmap_file_header = BitMapFileHeader(self.bitmap_file_header.size, self.bitmap_file_header.offset)

        img.bitmap_info_header.height = height
        img.bitmap_info_header.width = width
        img.bitmap_info_header.image_size = width*height*(img.bitmap_info_header.bit_count//8) # change for less bits

        img.bitmap_file_header.offset = 14 + img.bitmap_info_header.size
        if img.bitmap_info_header.bit_count == 24:
            img.bitmap_info_header.image_size += img.bitmap_info_header.width * 3 - 2
        img.bitmap_file_header.size = img.bitmap_file_header.offset + img.bitmap_info_header.image_size

        img.rgb = [[RGB()] for i in range(img.bitmap_info_header.height + 1)]
        for i in range(img.bitmap_info_header.height + 1):
            img.rgb[i] = [RGB() for j in range(img.bitmap_info_header.width)]

        if height>self.bitmap_info_header.height:
            counter_height = (height-self.bitmap_info_header.height)/self.bitmap_info_header.height
            height_bigger = True
        elif height< self.bitmap_info_header.height:
            counter_height = (self.bitmap_info_header.height-height)/self.bitmap_info_header.height
            height_bigger = False
        else:
            counter_height = 0
            height_bigger = True

        if width>self.bitmap_info_header.width:
            counter_width = (width - self.bitmap_info_header.width)/self.bitmap_info_header.width
            width_bigger = True
        elif width<self.bitmap_info_header.width:
            counter_width = (self.bitmap_info_header.width - width)/self.bitmap_info_header.width
            width_bigger = False
        else:
            counter_width = 0
            width_bigger = True

        counter_width_temp = counter_width
        counter_height_temp = counter_height
        source_i = 0

        for i in range(height):
            source_j = 0
            for j in range(width):
                img.rgb[i][j].blue = copy.deepcopy(self.rgb[source_i][source_j].blue)
                img.rgb[i][j].green = copy.deepcopy(self.rgb[source_i][source_j].green)
                img.rgb[i][j].red = copy.deepcopy(self.rgb[source_i][source_j].red)
                counter_width_temp += counter_width

                if width_bigger:
                    if counter_width_temp > 1:
                        counter_width_temp -= 1
                        if width_bigger and counter_width >= 1:
                            #counter_width_temp += 1
                            counter_width_temp -= int(counter_width)
                    else:
                        if source_j + 1 <= self.bitmap_info_header.width - 1:
                            source_j += 1
                else:
                    if source_j + 1 + int(counter_width_temp) <= self.bitmap_info_header.width - 1:
                        source_j += 1 + int(counter_width_temp)
                    else:
                        source_j = self.bitmap_info_header.width - 1
                    if counter_width_temp > 1:
                        if counter_width > 1:
                            counter_width_temp -= float(int(counter_width))
                        else:
                            counter_width_temp -= 1.0000001

            counter_height_temp += counter_height
            if height_bigger:
                if counter_height_temp > 1:
                    counter_height_temp -= 1
                    if counter_height >= 1:
                        counter_height_temp -= int(counter_height)
                else:
                    if source_i + 1 <= self.bitmap_info_header.height - 1:
                        source_i += 1
            else:
                if source_i + 1 + int(counter_height_temp) <= self.bitmap_info_header.height - 1:
                    source_i += 1 + int(counter_height_temp)
                else:
                    source_i = self.bitmap_info_header.height - 1
                if counter_height_temp > 1:
                    if counter_height > 1:
                        counter_height_temp -= int(counter_height)
                    else:
                        counter_height_temp -= 1.0000001
        return img


    def read_pixels_from_file(self, file):
        offset = self.bitmap_file_header.offset
        self.rgb = [[RGB()] for i in range(self.bitmap_info_header.height+1)]
        for i in range(self.bitmap_info_header.height+1):
            self.rgb[i] = [RGB() for j in range(self.bitmap_info_header.width)]   # make empty array of RGB-s
        if self.bitmap_info_header.bit_count == 24:
            color_counter = 3
            add = self.bitmap_info_header.width*3
            # add = 0
        elif self.bitmap_info_header.bit_count == 32:
            color_counter = 4
            add = 0
        else:
            color_counter = 3
            add = 0
            print("Something weird just happened! It's neither 32, nor 24 bit per pixel")
        overheight = False
        for i in range(0, self.bitmap_info_header.image_size+add, color_counter):
            width = (i//color_counter) % self.bitmap_info_header.width
            height = self.bitmap_info_header.height - (0 if add != 0 else 1) - (i//color_counter) // self.bitmap_info_header.width  # BTW somewhy bmp writes not left to right up to down, but l-to-r down-to-up. Why the hell?
            try:
                self.rgb[height][width].blue = ord(unpack('<c', file[0x0 + i + offset:0x0 + i + offset + 1])[0])  # And also it writes not r-g-b, but b-g-r. Why, why, for the love of god why???
                self.rgb[height][width].green = ord(unpack('<c', file[0x1 + i + offset:0x1 + i + offset + 1])[0])
                self.rgb[height][width].red = ord(unpack('<c', file[0x2 + i + offset:0x2 + i + offset + 1])[0])
            except struct.error:
                overheight = True
                pass
            if False:
                print(i)
            if False and height>400:
                print(width, end = " ")
                print(height, end =" ")
                print(self.rgb[height][width].blue)

        if overheight:
            self.bitmap_info_header.height -= 1
            self.rgb.pop(0)
        self.bitmap_info_header.image_size = self.bitmap_info_header.width * self.bitmap_info_header.size * self.bitmap_info_header.bit_count // 3
        self.bitmap_file_header.size = self.bitmap_file_header.offset + self.bitmap_info_header.image_size


#f = open_file("test.bmp")
#bm = read_file_header(f)
#ci = fill_core_info(f)
#print(bm.offset)
#print(ci.width)

#img1 = Image.read_from_file("test.bmp")
#img.test()
#img = img1.__copy__()
#print(img.rgb[450][333].red)
#print(img.rgb[450][333].green)
#print(img.rgb[450][333].blue)
#img32 = Image.read_from_file("test32.bmp")
#print(img32.rgb[499][333].red)
#print(img32.rgb[499][333].green)
#print(img32.rgb[499][333].blue)
#img.write_image("test_write.bmp")
#img32.write_image("test_write32.bmp")

#img_default = Image.set_default(255,20,20,24)
#img_sized = img_default.copy_with_changed_size(30, 20)
#img_sized.write_image("test_sized.bmp")
#img_downsized = img_default.copy_with_changed_size(10,10)
#img_downsized.write_image("test_sized_down.bmp")

img_default = Image.read_from_file("test40.bmp")
img_down = img_default.copy_with_changed_size(20, 60)
img_down.write_image("test_down.bmp")


def read_image(filename:str):
    img = Image.read_from_file(filename)
    return img


def generate_image(mode:int, width:int, height: int, bit_count:int = 24):
    img = Image.set_default(mode, width, height, bit_count)
    return img


def write_image(img: Image, filename:str):
    img.write_image(filename)


def copy_with_changed_size(img: Image, width:int, height:int):
    img_copy = img.copy_with_changed_size(width, height)
    return img_copy