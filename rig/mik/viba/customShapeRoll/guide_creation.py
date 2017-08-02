#!/usr/bin/env python
# coding:utf-8
""":mod:`guide_creation`
===================================
.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: viba
   :date: 2016.11

"""
import maya.cmds as mc


def create_guide_type(root=False, locator=False, name='guide01'):
    if root is True:
        create_root(name)
    elif locator is True:
        create_locator(name)


def create_root(name):
    mc.circle(n=name, r=2, nr=[0, 1, 0])
    mc.delete(name, ch=True)


def create_locator(name):
    mc.spaceLocator(n=name)