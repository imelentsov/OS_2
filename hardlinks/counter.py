#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2014-05-18 17:42
@summary: 
@author: i.melentsov
'''
import os
from texttable import Texttable
from collections import defaultdict

inodes = defaultdict(list)
visited_dirs_inodes = set()
symlinks = defaultdict(list)

def getInodes(dirName):
	if not os.path.isdir(dirName): # принимает символические ссылки и директории
		return
	try:
		for file in os.listdir(dirName):
			fileFullPath = dirName + os.sep + file;
			try:
				if os.path.isdir(fileFullPath):
					dirInode = os.stat(fileFullPath).st_ino
					if dirInode not in visited_dirs_inodes:
						visited_dirs_inodes.add(dirInode)
						getInodes(fileFullPath)
				else:
					inode = os.stat(fileFullPath).st_ino
					if os.path.islink(fileFullPath):
						symlinks[inode].append(fileFullPath + "(" + os.path.realpath(fileFullPath) + ")")
					else:
						inodes[inode].append(fileFullPath)
			except Exception:
				print ("Some errors occuried while getting stat info for {}".format(fileFullPath))
	except Exception:
		print("Cannot access path {}".format(dirName))


def main():
	getInodes(".")
	table = Texttable()
	table.set_cols_align(["l", "c", "c"])
	table.set_cols_valign(["t", "m", "m"])
	rows = [["File Names", "Inode", "Links Amount"]]
	rows.extend([ ("\n".join(inodes[inode] + symlinks[inode]), inode, len(inodes[inode])) for inode in inodes.viewkeys() | symlinks.viewkeys()])
	table.add_rows(rows)
	print (table.draw())


if __name__ == '__main__':
	main()
