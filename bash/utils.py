#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2014-05-22 12:49
@summary: 
@author: i.melentsov
'''

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)