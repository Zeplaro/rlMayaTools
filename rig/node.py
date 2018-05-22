import maya.cmds as mc
import os
import json
import math


def nodeToClass(node):
    node_type = mc.nodeType(node)
    if node_type == 'transform':
        return Transform(node)
    elif node_type == 'joint':
        return Joint(node)
    elif node_type == 'mesh':
        return Mesh(node)
    elif node_type == 'nurbsCurve':
        return NurbsCurve(node)
    elif node_type == 'skinCluster':
        return NurbsCurve(node)
    else:
        return DepNode(node)


def get_sel(flatten=True, long=True):
    return mc.sl(sl=True, flatten=flatten, long=long)


class DepNode(object):
    def __init__(self, node):
        self._name = node

    def __repr__(self):
        return self.name

    def __getitem__(self, keys):
        if isinstance(keys, basestring):
            keys = [keys]
        values = []
        keys = keys
        for key in keys:
            values.append(mc.getAttr('{}.{}'.format(self.name, key)))
        return values

    def __setitem__(self, keys, values):
        if isinstance(keys, basestring):
            keys = [keys]
            values = [values]
        for key, value in zip(keys, values):
            mc.setAttr('{}.{}'.format(self.name, key), value)

    def __bool__(self):
        return mc.objExists(self.name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        name = mc.rename(self.name, new_name)
        self._name = name

    @property
    def type(self):
        return mc.nodeType(self.name)


class DagNode(DepNode):
    def __init__(self, node):
        super(DagNode, self).__init__(node)

    @property
    def parent(self):
        return mc.listRelatives(self.name, p=True, fullPath=True)

    @parent.setter
    def parent(self, parent):
        if hasattr(parent, 'name'):
            parent = parent.name
        if parent:
            mc.parent(self.name, parent)
        else:
            mc.parent(self.name, w=True)
    @property
    def children(self):
        return mc.listRelatives(self.name, c=True, fullPath=True)


class Transform(DagNode):
    def __init__(self, obj):
        super(Transform, self).__init__(obj)
        print('Transform node initialized')

    @property
    def shapes(self):
        return mc.listRelatives(self.name, s=True, pa=1, ni=True) or []

    @property
    def matrix(self):
        return mc.getAttr('{}.matrix'.format(self.name))

    @property
    def worldMatrix(self):
        return mc.getAttr('{}.worldMatrix'.format(self.name))

    @property
    def translation(self):
        return mc.xform(self.name, q=True, os=True, t=True)

    @translation.setter
    def translation(self, value):
        mc.xform(self.name, os=True, t=value)

    @property
    def worldTranslation(self):
        return mc.xform(self.name, q=True, ws=True, t=True)

    @worldTranslation.setter
    def worldTranslation(self, value):
        mc.xform(self.name, ws=True, t=value)

    @property
    def rotation(self):
        return mc.xform(self.name, q=True, os=True, ro=True)

    @rotation.setter
    def rotation(self, value):
        mc.xform(self.name, os=True, ro=value)

    @property
    def worldRotation(self):
        return mc.xform(self.name, q=True, ws=True, ro=True)

    @worldRotation.setter
    def worldRotation(self, value):
        mc.xform(self.name, ws=True, ro=value)

    @property
    def scale(self):
        return mc.xform(self.name, q=True, os=True, s=True)

    @scale.setter
    def scale(self, value):
        mc.xform(self.name, os=True, s=value)

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

    @property
    def shear(self):
        return mc.xform(self.name, q=True, r=True, sh=True)

    @shear.setter
    def shear(self, value):
        mc.xform(self.name, r=True, sh=value)

    @property
    def magnitude(self):
        obj = self.translation
        mag = math.sqrt(pow(obj[0], 2) + pow(obj[1], 2) + pow(obj[2], 2))
        return mag

    def distance(self, obj):
        if hasattr(obj, 'worldTranslation'):
            obj = obj.worldTranslation
        else:
            obj = nodeToClass(obj).worldTranslation
        node = self.worldTranslation
        dist = math.sqrt(pow((obj[0] - node[0]), 2) + pow((obj[1] - node[1]), 2) + pow((obj[2] - node[2]), 2))
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
        grp = mc.group(em=True, n='{}_{}'.format(self.name, grp_suffix))
        grp = nodeToClass(grp)
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
            mir_node = nodeToClass(mir_node)
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
        mx = self.worldMatrix
        mxRot = mx[:3], mx[4:7], mx[8:11]

        axisDir = [0, 0, 0]
        for axis in range(3):
            values = mxRot[0][axis], mxRot[1][axis], mxRot[2][axis]  # Gathering values for each axis
            index = values.index(max(values, key=abs))  # Getting the index of the highest absolute value in values
            if index == 0:
                axisDir[axis] = 'x'
            elif index == 1:
                axisDir[axis] = 'y'
            else:
                axisDir[axis] = 'z'
            if values[index] < 0:
                axisDir[axis] = '-{}'.format(axisDir[axis])
        return axisDir



class Joint(Transform):
    def __init__(self, jnt):
        super(Joint, self).__init__(jnt)
        print('Joint node initialized')

    @property
    def jointOrient(self):
        return mc.getAttr('{}.jointOrient'.format(self.name))

    @jointOrient.setter
    def jointOrient(self, values):
        mc.setAttr('{}.jointOrient'.format(self.name), values)


class Shape(DagNode):
    def __init__(self, shape):
        super(Shape, self).__init__(shape)
        print('Shape node initialized')

    @property
    def skinCluster(self):
        skn = mc.ls(mc.listHistory(self.name, ac=True, pdo=True), type='skinCluster')
        if skn:
            return SkinCluster(skn[0])
        else:
            return None

    @property
    def parent(self):
        return mc.listRelatives(self.name, p=True, fullPath=True)

    @parent.setter
    def parent(self, parent):
        mc.parent(self.name, parent, r=True, s=True)


class NurbsCurve(Shape):
    def __init__(self, crv):
        super(NurbsCurve, self).__init__(crv)
        print('nurbsCurve node initialized')

    def __len__(self):
        return mc.getAttr('{}.spans'.format(self.name)) + mc.getAttr('{}.degree'.format(self.name))


class Mesh(Shape):
    def __init__(self, mesh):
        super(Mesh, self).__init__(mesh)
        print('Mesh node initialized')

    def __len__(self):
        return self.vtxs

    @property
    def vtxs(self):
        return mc.ls('{}.vtx[:]'.format(self.name), long=True, fl=True)

    @property
    def faces(self):
        return mc.ls('{}.f[:]'.format(self.name), long=True, fl=True)

    @property
    def edges(self):
        return mc.ls('{}.f[:]'.format(self.name), long=True, fl=True)


class SkinCluster(DepNode):
    def __init__(self, skn):
        super(SkinCluster, self).__init__(skn)
        print('SkinCluster node initialized')

    @property
    def infs(self):
        return mc.skinCluster(self.name, q=True, inf=True)

    @property
    def skinData(self):
        skinDict = {}
        skinDict['name'] = self.name
        skinDict['skinningMethod'] = self.skinningMethod
        skinDict['maximumInfluences'] = mc.skinCluster(self.name, q=True, mi=True)
        skinDict['normalizeWeights'] = mc.skinCluster(self.name, q=True, nw=True)
        skinDict['obeyMaxInfluences'] = mc.skinCluster(self.name, q=True, omi=True)
        skinDict['weightDistribution'] = mc.skinCluster(self.name, q=True, wd=True)
        skinDict['influences'] = {}
        for i, inf in enumerate(self.infs):
            skinDict['influences'][i] = {}
            skinDict['influences'][i]['index'] = i
            skinDict['influences'][i]['name'] = inf
            skinDict['influences'][i]['position'] = mc.xform(inf, q=True, ws=True, t=True)
        skinDict['skinWeights'] = self.skin_weights
        if skinDict['skinningMethod'] > 1:
            skinDict['dQWeigths'] = self.dQ_weights
        return skinDict

    @skinData.setter
    def skinData(self, data):
        mc.skinCluster(self.name, e=True,
                       sm=data['skinningMethod'],
                       mi=data['maximumInfluences'],
                       nw=0,
                       omi=data['obeyMaxInfluences'],
                       wd=data['weightDistribution'],
                       )
        self.skinningMethod = data['skinningMethod']
        self.skin_weights = data['skinWeights']
        if data['skinningMethod'] > 1:
            self.dQ_weights = data['dQWeigths']
            mc.setAttr('{}.dqsSupportNonRigid'.format(self.name), 1)
            mc.setAttr('{}.deformUserNormals'.format(self.name), 0)
        mc.skinCluster(self.name, e=True, nw=True)
        mc.skinCluster(self.name, e=True, forceNormalizeWeights=True)

    @property
    def skinningMethod(self):
        return mc.skinCluster(self.name, q=True, skinMethod=True)

    @skinningMethod.setter
    def skinningMethod(self, value):
        mc.setAttr('{}.skinningMethod'.format(self.name), value)

    @property
    def dQ_weights(self):
        dQ_weights = {}
        for i, comp in enumerate(mc.ls('{}.weightList[*]'.format(self.name))):
            dQ_weight = mc.getAttr('{}.blendWeights[{}]'.format(self.name, i))
            if dQ_weight:
                dQ_weights[i] = dQ_weight
        return dQ_weights

    @dQ_weights.setter
    def dQ_weights(self, data):
        for comp, weight in data.iteritems():
            mc.setAttr('{}.blendWeights[{}]'.format(self.name, comp), weight)
        for i, comp in enumerate(mc.ls('{}.weightList[*]'.format(self.name))):
            if str(i) not in data:
                mc.setAttr('{}.blendWeights[{}]'.format(self.name, i), 0)

    @property
    def skin_weights(self):
        weightDict = {}
        for i, comp in enumerate(mc.ls('{}.weightList[*]'.format(self.name))):
            weightDict[i] = {}
            for j, jnt in enumerate(self.infs):
                weight = mc.getAttr('{}.weightList[{}]weights[{}]'.format(self.name, i, j))
                if weight:
                    weightDict[i][j] = weight
        return weightDict

    @skin_weights.setter
    def skin_weights(self, data):
        for comp, infs in data.iteritems():
            for inf, weight in infs.iteritems():
                mc.setAttr('{}.weightList[{}]weights[{}]'.format(self.name, comp, inf), weight)
            for i, inf in enumerate(self.infs):
                if str(i) not in infs:
                    mc.setAttr('{}.weightList[{}]weights[{}]'.format(self.name, comp, i), 0)

    @staticmethod
    def load_skin_file(path, fileName):
        fullPath = os.path.join(path, fileName)
        with open(fullPath, 'r') as skinFile:
            data = json.load(skinFile)
        print(data)
        return data

    def save_skin_file(self, path, fileName):
        fullPath = os.path.join(path, fileName)
        with open(fullPath, 'w') as skinFile:
            json.dump(self.skinData, skinFile, indent=2)

    def reSkin(self):
        for inf in self.infs:
            conns = mc.listConnections('{}.worldMatrix'.format(inf), type='skinCluster', p=True)
            for conn in conns:
                bpm = conn.replace('matrix', 'bindPreMatrix')
                wim = mc.getAttr('{}.worldInverseMatrix'.format(inf))
                if not mc.listConnections(bpm):
                    mc.setAttr(bpm, *wim, type='matrix')
                else:
                    print('{} is connected'.format(bpm))
        mc.skinCluster(self.name, e=True, rbm=True)

