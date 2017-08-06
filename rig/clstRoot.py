import maya.cmds as mc
from tbx import get_shape

def do_clstRoot(clsts=None):

    if not clsts:
        clsts = [x for x in mc.ls(sl=True) if 'clusterHandle' in (mc.nodeType(get_shape(x), i=True) or [])]

    if not clsts:
        mc.warning('No cluster selected')
        return

    for clst_handle in clsts:

        cluster = mc.listConnections(clst_handle, d=True, scn=True)[0]
        clst_handle_shape = get_shape(clst_handle)[0]
        if not cluster or not clst_handle_shape:
            mc.warning('No cluster node found on '+clst_handle)
            continue
        new_name = clst_handle.replace('Handle', '')
        ro = mc.xform(clst_handle, q=1, ro=True)
        roP = mc.xform(clst_handle, q=1, rotatePivot=True)
        t = mc.xform(clst_handle, q=1, translation=True)
        t = [x + y for x, y in zip(t, roP)]

        root_grp = mc.group(em=True, w=True, n=new_name+'_root')
        cluster_grp = mc.group(em=True, parent=root_grp, n=new_name+'#')
        mc.xform(root_grp, ws=True, t=t)
        mc.xform(cluster_grp, ws=True, ro=ro)

        mc.connectAttr(cluster_grp+'.worldMatrix[0]', cluster+'.matrix', force=True)
        mc.connectAttr(cluster_grp+'.matrix', cluster+'.weightedMatrix', force=True)
        mc.connectAttr(root_grp+'.worldInverseMatrix[0]', cluster+'.bindPreMatrix', force=True)
        mc.connectAttr(root_grp+'.worldInverseMatrix[0]', cluster+'.preMatrix', force=True)

        mc.disconnectAttr(clst_handle_shape+'.clusterTransforms[0]', cluster+'.clusterXforms')
        mc.delete(clst_handle_shape, clst_handle)
