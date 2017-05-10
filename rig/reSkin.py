import maya.cmds as mc
import utils as ut


def do_reSkin(objs=None):

    if not objs:
        objs = mc.ls(sl=True, fl=True)
    for obj in objs:
        skn = ut.getSkinCluster(obj)
        infs = mc.skinCluster(skn, q=True, inf=True)
        for inf in infs:
            conns = mc.listConnections(inf+'.worldMatrix', type='skinCluster', p=True)
            for conn in conns:
                bpm = conn.replace('matrix', 'bindPreMatrix')
                wim = mc.getAttr(inf+'.worldInverseMatrix')
                mc.setAttr(bpm, wim, type='matrix')
        mc.skinCluster(skn, e=True, rbm=True)
