import maya.cmds as mc
import node.dag as dag
import node as nd
import math


class Transform(dag.Dag):
    def __init__(self, obj):
        super(Transform, self).__init__(obj)

    @property
    def shapes(self):
        return mc.listRelatives(self.name, s=True, pa=1, ni=True) or []

    @property
    def worldTranslation(self):
        return mc.xform(self.name, q=True, ws=True, t=True)

    @worldTranslation.setter
    def worldTranslation(self, value):
        mc.xform(self.name, ws=True, t=value)

    @property
    def worldRotation(self):
        return mc.xform(self.name, q=True, ws=True, ro=True)

    @worldRotation.setter
    def worldRotation(self, value):
        mc.xform(self.name, ws=True, ro=value)

    @property
    def worldScale(self):
        return mc.xform(self.name, q=True, ws=True, s=True)

    @worldScale.setter
    def worldScale(self, value):
        mc.xform(self.name, ws=True, s=value)

    @property
    def rotatePivot(self):
        return mc.xform(self.name, q=True, os=True, rp=True)

    @rotatePivot.setter
    def rotatePivot(self, value):
        mc.xform(self.name, os=True, rp=value)

    @property
    def worldRotatePivot(self):
        return mc.xform(self.name, q=True, ws=True, rp=True)

    @worldRotatePivot.setter
    def worldRotatePivot(self, value):
        mc.xform(self.name, ws=True, rp=value)

    def distance(self, obj):
        if hasattr(obj, 'worldTranslation'):
            obj = obj.worldTranslation
        else:
            obj = nd.node_to_class(obj).worldTranslation
        node_wt = self.worldTranslation
        dist = math.sqrt(pow(node_wt[0] - obj[0], 2) + pow(node_wt[1] - obj[1], 2) + pow(node_wt[2] - obj[2], 2))
        return dist

    def add_shape(self, shape):
        mc.parent(shape, self.name, r=True, s=True)

    def add_shapes(self, shapes):
        for shape in shapes:
            self.add_shape(shape)

    def reset_local_pivot(self):
        pivot = mc.group(em=True, w=True, n='{}_pivot_grp#'.format(self.name))
        mc.delete(mc.parentConstraint(self.name, pivot, mo=False))
        dad = self.parent
        self.parent = pivot
        mc.makeIdentity(a=True, r=False, s=False, t=True)
        if dad:
            self.parent = dad
        else:
            self.parent = '|'
        mc.delete(pivot)

    def add_group(self, grp_suffix='orig'):
        if mc.objExists('{}_{}'.format(self.name, grp_suffix)):
            grp_suffix += '#'
        grp = mc.group(em=True, n='{}_{}'.format(self.name, grp_suffix))
        grp = nd.node_to_class(grp)
        if self.parent:
            grp.parent = self.parent
        grp.worldTranslation = self.worldTranslation
        grp.worldRotation = self.worldRotation
        grp.worldScale = self.worldScale
        self.parent = grp
        return grp

    def add_groups(self, nbr=1, grp_suffix='orig'):
        grps = []
        for i in range(nbr):
            grp = self.add_group(grp_suffix=grp_suffix)
            grps.append(grp)
        return grps

    def get_mirror_table(self, mir_node, miraxis='x'):
        """
        Return a mirror table between two object on chosen axis
        :param str mir_node: object to compare to self
        :param str miraxis: 'x'(default) chosen world axis on wich mirror to mirror
        :return: list: return a mirror table list, e.g.:[-1, 1, 1]
        """
        orient = self.get_world_orientation()
        if not hasattr(mir_node, 'worldMatrix'):
            mir_node = nd.node_to_class(mir_node)
        mir_node_orient = mir_node.get_world_orientation()
        mirtable = [1, 1, 1]
        for i in range(3):
            if orient[i][-1] == mir_node_orient[i][-1]:
                if not orient[i][0] == mir_node_orient[i][0]:
                    mirtable[i] = -1
                if orient[i][-1] == miraxis:
                    mirtable[i] *= -1
            else:
                mirtable[i] = 0
        return mirtable

    def get_world_orientation(self):
        """
        Return a list of axis direction compared to the world
        :return: list: return an axis direction list compared to world,
                        first index giving the x axis direction and so on e.g.:[y, -z, -x],
                        for a object matching world axis it will return : [x, y, z]
        """
        mx = self['worldMatrix']
        mx_rot = mx[:3], mx[4:7], mx[8:11]

        axis_dir = [0, 0, 0]
        for axis in range(3):
            values = mx_rot[0][axis], mx_rot[1][axis], mx_rot[2][axis]  # Gathering values for each axis
            index = values.index(max(values, key=abs))  # Getting the index of the highest absolute value in values
            if index == 0:
                axis_dir[axis] = 'x'
            elif index == 1:
                axis_dir[axis] = 'y'
            else:
                axis_dir[axis] = 'z'
            if values[index] < 0:
                axis_dir[axis] = '-{}'.format(axis_dir[axis])
        return axis_dir

    def create_hook(self, suffix_name='hook', parent=None):
        if mc.objExists('{}_{}'.format(self.name, suffix_name)):
            suffix_name += '#'
        hook = mc.group(em=True, n='{}_{}'.format(self.name, suffix_name))
        mmx = mc.createNode('multMatrix', n='mmx_{}_{}'.format(self.name, suffix_name))
        dmx = mc.createNode('decomposeMatrix', n='dmx_{}_{}'.format(self.name, suffix_name))
        mc.connectAttr('{}.worldMatrix[0]'.format(self.name), '{}.matrixIn[1]'.format(mmx), f=True)
        mc.connectAttr('{}.parentInverseMatrix[0]'.format(hook), '{}.matrixIn[2]'.format(mmx), f=True)
        mc.connectAttr('{}.matrixSum'.format(mmx), '{}.inputMatrix'.format(dmx), f=True)
        mc.connectAttr('{}.outputShear'.format(dmx), '{}.shear'.format(hook), f=True)
        mc.connectAttr('{}.outputTranslate'.format(dmx), '{}.translate'.format(hook), f=True)
        mc.connectAttr('{}.outputScale'.format(dmx), '{}.scale'.format(hook), f=True)
        mc.connectAttr('{}.outputRotate'.format(dmx), '{}.rotate'.format(hook), f=True)
        if parent and mc.objExists(parent):
            mc.parent(hook, parent)
        return hook
