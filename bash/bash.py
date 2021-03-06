#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2014-05-22 10:59
@summary: 
@author: i.melentsov
'''

import os, signal
from sys import stdin, stdout
from pypeg2 import *
from utils import *

arg = re.compile("(?:\w|[-\"'/.\\\,])+")
filename = re.compile("(?:\w|\.|/)*(?:\w|\.)+")

Direction = enum("LEFT", "RIGHT")

""" перенаправления """
class Redirection(object):
	def getDirection(self):
		pass

class LRedirection(Redirection):
	grammar = "<", attr("file", filename)

	def getDirection(self):
		return Direction.LEFT

class RRedirection(Redirection):
	grammar = ">", attr("file", filename)

	def getDirection(self):
		return Direction.RIGHT

class Element(object):
	current_pgrp = 0

	def run(self):
		if hasattr(self, "group"):
			Element.current_pgrp = 0

		if self.pipe is not None:
			pipeIn, pipeOut = os.pipe()
			pid = os.fork()
			if pid:
				# parent
				os.close(pipeOut)
				os.dup2(pipeIn, 0)
				if not Element.current_pgrp:
					Element.current_pgrp = pid
				self.pipe.run()
			else:
				# child
				os.close(pipeIn)
				os.dup2(pipeOut, 1)
				self.runNext()
		else:
			pid = os.fork()
			if pid:
				# parent
				try:
					while True:
						os.wait() # если потомков не осталось выбросит исключение (Errno = -1)
				except Exception:
					pass
			else:
				# child
				self.runNext()

		if self.semicolon is not None:
				Element.current_pgrp = 0

	def runNext(self):
		if hasattr(self, "group"):
			self.group.run()			
		elif hasattr(self, "command"):
			while True: # жесть конечно, но иначе не знаю как контролировать что группа создана
				try:
					os.setpgid(0, Element.current_pgrp)
					break
				except:
					pass
			self.command.run()
		else: #hasattr(self, "redirections")
			self.redirections.run()

class ElementWithRedirection(Element):
	grammar = attr("redirections", some([LRedirection, RRedirection]))
	
	def getRedirections(self, direction):
		return list(filter(lambda x: x.getDirection() == direction, [] if self.redirections is None else self.redirections))

	""" устанавливает перенаправления перед исполнением комманды """
	def setCommandRedirections(self):
		for fileIn in self.getRedirections(Direction.LEFT):
			os.dup2(os.open(fileIn.file, os.O_CREAT | os.O_RDONLY), 0)
		for fileOut in self.getRedirections(Direction.RIGHT):
			os.dup2(os.open(fileOut.file, os.O_CREAT | os.O_WRONLY), 1)

	def run(self):
		self.setCommandRedirections()

""" исполняемая команда """
class Command(ElementWithRedirection):
	grammar = attr("name", filename), attr("args", maybe_some(arg)), attr("redirections", maybe_some([LRedirection, RRedirection]))

	def run(self):
		self.setCommandRedirections()
		self.args.insert(0, self.name)
		os.execvp(self.name, self.args)

""" последовательно обрабатываемые элементы, разделяемые ';'' """
class Elements(List, Element):
	def run(self):
		for element in self:			
			if element is not None:
				element.run()

class Group(ElementWithRedirection):
	def run(self):
		self.setCommandRedirections()
		# запустить subshell
		subtree = Elements()
		subtree += self.elements
		startElementsInit(subtree)
		exit(0)

class Piped(Element):
	def run(self):
		for element in self.piped:			
			if element is not None:
				element.run()

Element.grammar = [ attr("group", Group), attr("command", Command), attr("redirections", ElementWithRedirection) ], attr("semicolon", optional(";")), attr("pipe", optional(Piped))
Piped.grammar = '|', attr("piped", (Element, Elements))
Group.grammar = "(", attr("elements", (Element, Elements)), ")", attr("redirections", maybe_some([LRedirection, RRedirection]))
Elements.grammar = [ (Element, Elements), None ]

creatorPID = None

# fork-нуться и стать лидером сессии
def startElementsInit(tree):
	global creatorPID
	pid = os.fork()
	if pid:
		# parent
		try:
			creatorPID = pid
			os.waitpid(pid, 0)
			creatorPID = None
		except Exception:
			pass
	else:
		# child - root for all other processes (bash)
		signal.signal(signal.SIGCHLD, signal.SIG_DFL)
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		creatorPID = os.getpid()
		os.setsid()
		tree.run()
		exit(0)

def sigchldHandler(signum, frame):
	try:
		os.wait()
	except Exception:
		pass

def sigintHandler(signum, frame):
	global creatorPID
	if creatorPID is not None:
		try:
			os.kill(creatorPID, signal.SIGINT)
		except:
			exit(0)
	else:
		exit(0)

def bash():
	signal.signal(signal.SIGCHLD, sigchldHandler)
	signal.signal(signal.SIGINT, sigintHandler)

	while True:
		command = input("> ")
		if "exit" == command:
			break
		tree = []
		try:
			tree = parse(command, Elements)
		except Exception as e:
			print("Syntax error: {}".format(e))
			continue
		try:
			startElementsInit(tree)
		except Exception as e:
			print("Could not execute statement: {}".format(e))

if __name__ == '__main__':
	bash()