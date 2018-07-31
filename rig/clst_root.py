import maya.cmds as mc
from tbx import get_shape


def clst_root(clsts=None):

    if not clsts:
        clsts = [x for x in mc.ls(sl=True) if 'clusterHandle' in (mc.nodeType(get_shape(x), i=True) or [])]

    if not clsts:
        mc.warning('No cluster selected')
        return

    for clst_handle in clsts:

        cluster = mc.listConnections(clst_handle, d=True, scn=True)[0]
        clst_handle_shape = get_shape(clst_handle)[0]
        if not cluster or not clst_handle_shape:
            mc.warning('No cluster node found on {}'.format(clst_handle))
            continue
        new_name = clst_handle.replace('Handle', '')
        ro = mc.xform(clst_handle, q=True, ro=True)
        rop = mc.xform(clst_handle, q=True, rotatePivot=True)
        t = mc.xform(clst_handle, q=True, translation=True)
        t = [x + y for x, y in zip(t, rop)]

        root_grp = mc.group(em=True, w=True, n='{}_root'.format(new_name))
        cluster_grp = mc.group(em=True, parent=root_grp, n='{}#'.format(new_name))
        mc.xform(root_grp, ws=True, t=t)
        mc.xform(cluster_grp, ws=True, ro=ro)

        mc.connectAttr('{}.worldMatrix[0]'.format(cluster_grp), '{}.matrix'.format(cluster), force=True)
        mc.connectAttr('{}.matrix'.format(cluster_grp), '{}.weightedMatrix'.format(cluster), force=True)
        mc.connectAttr('{}.worldInverseMatrix[0]'.format(root_grp), '{}.bindPreMatrix'.format(cluster), force=True)
        mc.connectAttr('{}.worldInverseMatrix[0]'.format(root_grp), '{}.preMatrix'.format(cluster), force=True)

        mc.disconnectAttr('{}.clusterTransforms[0]'.format(clst_handle_shape), '{}.clusterXforms'.format(cluster))
        mc.delete(clst_handle_shape, clst_handle)
