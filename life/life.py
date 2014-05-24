#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2014-05-24 01:34
@summary: 
@author: i.melentsov
'''

import os
import time
import mmap
import select
import socket
from texttable import Texttable

class Life(object):
	def __init__(self, cells, size=15):
		self.cells = cells
		self.size = size
		self.stateChanged = True
		self.isCellAlive = lambda cell: cell in self.cells

	def makeStep(self):
		self.stateChanged = False
		newCells = set()
		processed = set()
		for liveCell in self.cells:
			if self.isCellGonnaBeAlive(liveCell):
				newCells.add(liveCell)
			else:
				self.stateChanged = True 
			for neighbour in self.getUnaliveNeighbours(liveCell):
				if neighbour not in processed:
					processed.add(neighbour)
					if self.isCellGonnaBeAlive(neighbour):
						newCells.add(neighbour)
						self.stateChanged = True 
		self.cells = newCells
				
	def isCellGonnaBeAlive(self, cell):
		isAlive = self.isCellAlive(cell)
		aliveNeighbours = len(self.getAliveNeighbours(cell))
		return (isAlive and 2 <= aliveNeighbours <= 3) or (not isAlive and aliveNeighbours == 3)

	def getUnaliveNeighbours(self, cell):
		return self.getNeighbourCells(cell) - self.getAliveNeighbours(cell)

	def getAliveNeighbours(self, cell):
		return set([neighbour for neighbour in self.getNeighbourCells(cell) if self.isCellAlive(neighbour)])

	def getNeighbourCells(self, cell):
		(x, y) = cell
		return set(filter(lambda x: True if (x[0]>=0 and x[0]<self.size and x[1]>=0 and x[1]<self.size) else False,
				[(x-1, y-1), (x-1, y), (x-1, y+1), (x, y-1), (x, y+1), (x+1, y-1), (x+1, y), (x+1, y+1)]))

	def isFinished(self):
		return not self.stateChanged

	def toString(self):
		table = Texttable()
		table.set_chars(['-','|','+','-'])
		rows = []
		for i in range(0, self.size):
			row = []
			for j in range(0, self.size):
				row.append("x" if (i, j) in self.cells else "o")
			rows.append(row)
		table.add_rows(rows)
		return table.draw()

class LifeServer(object):

	def __init__(self, game, port=8080, listen=5):
		self.game = game
		self.port = port
		self.listen = listen

		self.buffer = mmap.mmap(-1, mmap.PAGESIZE)

	def start(self):
		if os.fork():
			self.generate()
		else:
			self.communicate()

	def generate(self):
		if not self.game.isFinished():
			time.sleep(1)
			self.game.makeStep()
			self.buffer.seek(0)
			self.buffer.write(self.game.toString())
			self.generate()

	def communicate(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind(('', self.port))
		server.listen(self.listen)
		print("Server started on port - {}".format(self.port))

		while True:
			readable, writable, errored = select.select([server], [], [], 0)
			for rs in readable:
				client, address = server.accept()
				print("New client accepted from - {}".format(address))

				self.buffer.seek(0)
				client.send(self.buffer.read(mmap.PAGESIZE))
				client.shutdown(socket.SHUT_RDWR)
				client.close()

def main():
	game = Life(set([(1, 2), (2, 3), (3, 1), (3, 2), (3, 3)]))
	server = LifeServer(game)
	server.start()

if __name__ == '__main__':
	main()