import maya.cmds as mc


def reskin():
    obj=mc.ls(sl=1,sn=1,typ=mesh)

mc.listRelatives(master, c=1, s=1, pa=1, type='nurbsCurve')