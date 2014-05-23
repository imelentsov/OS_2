#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2014-05-18 09:48
@summary: 
@author: i.melentsov
'''
import sys
import Image
from collections import defaultdict

class Finder(object):
	def __init__(self, imagename):
		image = Image.open(imagename)
		self.width, self.height = image.size
		self.pixels = image.load()

	def get_red_point(self):
		answers = defaultdict(int)
		# ищем квадрат такого размера с самым насыщенным красным цветом
		square_w, square_h = 42, 28
		halh_square_w, halh_square_h = square_w >> 1, square_h >> 1
		red_max = 0
		key_max = (0, 0)
		for x in range(-halh_square_w, self.width):
			add = 0
			minus_column = x - halh_square_w - 1
			plus_column = x + halh_square_w
			for y in range(0, halh_square_h):
				if(minus_column >= 0):
					add -= self._is_red(minus_column, y)
				if(plus_column < self.width):
					add += self._is_red(plus_column, y)
			for y in range(0, self.height):
				if (minus_column >= 0):
					if (y - halh_square_h - 1 >= 0):
						add += self._is_red(minus_column, y - halh_square_h - 1)
					if (y + halh_square_h < self.height):
						add -= self._is_red(minus_column, y + halh_square_h)
				if (plus_column < self.width):
					if (y + halh_square_h < self.height):
						add += self._is_red(plus_column, y + halh_square_h)
					if (y - halh_square_h - 1 >= 0):
						add -= self._is_red(plus_column, y - halh_square_h - 1)
				answers[y] = answers[y] + add
				if (red_max < answers[y]):
					red_max = answers[y]
					key_max = (x, y)			
		return key_max

	def _is_red(self, xx, yy):
		red, green, blue = self.pixels[xx, yy]
		return 200 < red and blue + green < 60


def main():
	imagename = sys.argv[1]
	finder = Finder(imagename)
	x, y = finder.get_red_point()
	print("{} {}".format(x, y))


if __name__ == '__main__':
	main()
