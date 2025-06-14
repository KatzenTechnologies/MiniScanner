import colorsys
import math


class Color:
    def __rs(self, x, y):
        chunks = len(x)
        chunk_size = len(x) // y - 1
        return [x[i:i + chunk_size] for i in range(0, chunks, chunk_size)]
    def __color_check(self,
                      canal):
        if self.__color[canal] > 255:
            self.__color[canal] = 255
        elif self.__color[canal] < 1:
            self.__color[canal] = 0
    def __init__(self,
                 hex = None,
                 rgb = None,
                 hsv = None):
        self.__color = []

        if hex is not None:
            if hex.find("#") == 0:
                hex = hex[1:]

            self.__color = list(map(lambda x: ord(bytes.fromhex(x)), self.__rs(hex, 2)))
        elif rgb is not None:
            self.__color = list(rgb)
            for i in range(3): self.__color_check(i)
        elif hsv is not None:
            self.__color = list(colorsys.hsv_to_rgb(hsv[0],hsv[1],hsv[2]))



    def hex(self):
        self.__color = list(map(int,self.__color))
        turnback = "#{:02x}{:02x}{:02x}".format(self.__color[0],
                                                self.__color[1],
                                                self.__color[2])
        return turnback

    def rgb(self):
        return tuple(self.__color)

    def hsv(self):
        return colorsys.rgb_to_hsv(self.__color[0],
                                   self.__color[1],
                                   self.__color[2])



    def append(self,
               canal: int,
               append_value: int) -> None:
        self.__color[canal] += append_value

        self.__color_check(canal)

    def append_multi(self,
                     canals: list | tuple,
                     append_value: int) -> None:
        for i in canals:
            self.append(i,append_value)

    def use(self,
               canal: int,
               function) -> None:
        self.__color[canal] = function(self.__color[canal])

        self.__color_check(canal)

class Fade:
    def __init__(self,
                 color1: Color,
                 color2: Color):
        self.color1 = color1.rgb()
        self.color2 = color2.rgb()

    def generate(self, lines: int):
        if not lines in [0, 1, 2]:
            lines = lines - 2
        else:
            lines = 3
        result = [Color(rgb = self.color1)]

        delta_r = self.color2[0] - self.color1[0]
        delta_g = self.color2[1] - self.color1[1]
        delta_b = self.color2[2] - self.color1[2]

        add_value_r = int(round(delta_r / lines, 0))
        add_value_g = int(round(delta_g / lines, 0))
        add_value_b = int(round(delta_b / lines, 0))

        r = self.color1[0]
        g = self.color1[1]
        b = self.color1[2]

        for i in range(lines):
            r += add_value_r
            g += add_value_g
            b += add_value_b
            result.append(Color(rgb=(r, g, b)))

        result.append(Color(rgb=self.color2))

        return result

def darker(color, value):
    if value >= 0:
        value = -value
        
    color.append_multi([0, 1, 2], value)
    
    return color

WHITE   = Color(hex="ffffff")
BLACK   = Color(hex="000000")
RED     = Color(hex="ff0000")
GREEN   = Color(hex="00ff00")
BLUE    = Color(hex="0000ff")
YELLOW  = Color(hex="ffff00")
ORANGE  = Color(hex="ff9900")
PINK    = Color(hex="ff33cc")
PURPLE  = Color(hex="cc00cc")
PINK2   = Color(hex="ff0066")
AQUA    = Color(hex="00ffff")
