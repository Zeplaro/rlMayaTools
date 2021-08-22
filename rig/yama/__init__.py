import maya.cmds as mc
import nodes.dependNode as dpn


yam = dpn.yam
yams = dpn.yams


def ls(*args, **kwargs):
    return yams(mc.ls(*args, **kwargs))


def selected():
    return yams(mc.ls(sl=True, fl=True))
