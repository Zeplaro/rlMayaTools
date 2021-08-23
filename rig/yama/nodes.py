# encoding: utf8

import maya.cmds as mc
import maya.mel as mel
import maya.api.OpenMaya as om
from math import sqrt

import weightsdict as wdt

try:
    basestring
except NameError:
    basestring = str


def yam(node):
    """
    Handles all node class assignment to assign the proper class depending on the node type.
    todo : make it works when an attribute is given.

    exemples :
    >> yam('skincluster42')
    SkinCluster('skincluster42')

    todo:
    >> yam('null0.translateX')
    Attribute('null0.translateX')
    """

    # Lists the supported types of maya nodes. Any new node class should be added to this list to be able to get it from
    # the yam method. Follow this syntax -> 'mayaType': class)
    suported_class = {'skinCluster': SkinCluster,
                      'shape': Shape,
                      'mesh': Mesh,
                      'nurbsCurve': NurbsCurve,
                      'geometryFilter': GeometryFilter,
                      'weightGeometryFilter': WeightGeometryFilter,
                      'blendShape': BlendShape,
                      'transform': Transform,
                      'joint': Joint,
                      }

    attr = None
    if isinstance(node, basestring):
        if '.' in node:  # checking if an attribute was given with the node
            split = node.split('.')
            node = split.pop(0)
            attr = '.'.join(split)
        s = om.MSelectionList()
        try:
            s.add(node)
        except RuntimeError:
            if mc.objExists(node):
                raise RuntimeError("more than one object called '{}'".format(node))
            raise RuntimeError("No '{}' object found in scene".format(node))
        dagPath = s.getDagPath(0)
        mObject = dagPath.node()
    elif isinstance(node, om.MObject):
        mObject = node
    elif isinstance(node, om.MDagPath):
        mObject = node.node()
    else:
        raise TypeError("yam() str or OpenMaya.MObject of OpenMaya.MDagPath expected,"
                        " got {}.".format(node.__class__.__name__))

    # checking if node type is a supported class, if not defaults to DependNode
    node_class = DependNode
    partialPathName = om.MDagPath.getAPathTo(mObject).partialPathName()
    for node_type in mc.nodeType(partialPathName, i=True)[::-1]:
        if node_type in suported_class:
            node_class = suported_class[node_type]
            break
    if attr is not None:
        return node_class(node).attr(attr)
    return node_class(node)


def yams(nodes):
    return [yam(node) for node in nodes]


class DependNode(object):
    def __init__(self, mObject):
        self._mObject = mObject
        self._mFnDependencyNode = None
        self._mDagPath = None

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, self.name)

    def __str__(self):
        return self.name

    def __getattr__(self, attr):
        return self.attr(attr)

    def __radd__(self, other):
        if isinstance(other, basestring):
            return other.__add__(self.name)
        else:
            raise TypeError("cannot concatenate '{}' and '{}' objects".format(other.__class__.__name,
                                                                              self.__class__.__name__))

    @property
    def mObject(self):
        return self._mObject

    @property
    def mDagPath(self):
        if self._mDagPath is None:
            self._mDagPath = om.MDagPath.getAPathTo(self._mObject)
        return self._mDagPath

    @property
    def mFnDependencyNode(self):
        if self._mFnDependencyNode is None:
            self._mFnDependencyNode = om.MFnDependencyNode(self._mObject)
        return self._mFnDependencyNode

    @property
    def name(self):
        return self.mFnDependencyNode.name()

    @name.setter
    def name(self, value):
        self.mFnDependencyNode.setName(value)

    def attr(self, attr):
        import attribute
        return attribute.Attribute(self, attr)

    def listRelatives(self, *args, **kwargs):
        return yams(mc.listRelatives(self, *args, **kwargs) or [])

    def type(self):
        return self.mFnDependencyNode.typeName


class Transform(DependNode):
    def __init__(self, mObject):
        super(Transform, self).__init__(mObject)

    def children(self):
        return yams(self.mDagPath.child(x) for x in range(self.mDagPath.childCount()))

    def get_shapes(self):
        return self.listRelatives(s=True)

    @property
    def shape(self):
        shapes = self.get_shapes()
        return shapes[0] if shapes else None

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
        if isinstance(obj, Transform):
            wt = obj.worldTranslation
        elif isinstance(obj, basestring):
            wt = yam(obj).worldTranslation
        else:
            raise AttributeError("wrong type given, expected : 'Transform' or 'str', "
                                 "got : {}".format(obj.__class__.__name__))
        node_wt = self.worldTranslation
        dist = sqrt(pow(node_wt[0] - wt[0], 2) + pow(node_wt[1] - wt[1], 2) + pow(node_wt[2] - wt[2], 2))
        return dist


class Joint(Transform):
    def __init__(self, mObject):
        super(Transform, self).__init__(mObject)


class Shape(DependNode):
    def __init__(self, mObject):
        super(Shape, self).__init__(mObject)

    def get_components(self):
        raise NotImplementedError

    def __len__(self):
        return len(self.get_components())


class Mesh(Shape):
    def __init__(self, mObject):
        super(Mesh, self).__init__(mObject)

    def get_components(self):
        return mc.ls(self.name + '.vtx[*]', fl=True)

    def get_component_indexes(self):
        for i in range(len(self)):
            yield i


class NurbsCurve(Shape):
    def __init__(self, mObject):
        super(NurbsCurve, self).__init__(mObject)

    def __len__(self):
        return self.spans.value + self.degree.value

    def get_components(self):
        return mc.ls(self.name + '.cv[*]', fl=True)

    def get_component_indexes(self):
        for i in range(len(self)):
            yield i

    @property
    def cps(self):
        cps = mc.ls('{}.cp[:]'.format(self.name), flatten=True)
        cps = [x.replace('.cv', '.cp') for x in cps]
        return cps

    @staticmethod
    def get_control_point_position(controls):
        return [mc.xform(x, q=True, os=True, t=True) for x in controls]

    @staticmethod
    def set_control_point_position(controls, positions):
        [mc.xform(control, os=True, t=position) for control in controls for position in positions]

    @property
    def arclen(self):
        return mc.arclen(self.name)

    @property
    def data(self):
        # todo: copied form old node work, needs cleanup
        data = {'name': self.name,
                'type': self.type,
                'spans': self.spans.value,
                'form': self.form.value,
                'degree': self.degree.value,
                'cps': self.get_control_point_position(self.cps),
                'knots': self.knots
                }
        return data

    @data.setter
    def data(self, data):
        # todo: copied form old node work, needs cleanup
        for d in data:
            setattr(d, data[d])

    @property
    def knots(self):
        # todo: copied form old node work, needs cleanup
        nb_knots = len(self) + self.degree.value - 1
        print('Nb of knots: {}'.format(nb_knots))

        if self.form.value == 0:
            knots = list(range(nb_knots-(self.degree.value - 1) * 2))
            for i in range(self.degree.value - 1):
                knots = knots[:1] + knots
                knots += knots[-1:]
        else:
            knots = list(range(nb_knots-(self.degree.value - 1)))
            for i in range(self.degree.value - 1):
                knots.insert(0, knots[0]-1)

        if self.type == 'bezierCurve':
            knots = []
            for i in range(nb_knots/3):
                for j in range(3):
                    knots.append(i)
        knots = [float(x) for x in knots]
        return knots


class GeometryFilter(DependNode):
    def __init__(self, mObject):
        super(GeometryFilter, self).__init__(mObject)

    @property
    def geometry(self):
        geo = mc.deformer(self.name, q=True, geometry=True)
        return yam(geo[0]) if geo else None


class WeightGeometryFilter(GeometryFilter):
    def __init__(self, mObject):
        super(WeightGeometryFilter, self).__init__(mObject)

    @property
    def weights(self):
        weights = wdt.WeightsDict(self)
        for i in self.geometry.get_components_index():
            weights[i] = self.weights_attr(i).value
        return weights

    @weights.setter
    def weights(self, weights):
        for i, weight in weights.items():
            self.weights_attr(i).value = weight

    def weights_attr(self, index):
        return self.weightList[0].weights[index]


class SkinCluster(GeometryFilter):
    def __init__(self, mObject):
        super(SkinCluster, self).__init__(mObject)
        self._weights_attr = None

    def influences(self):
        return yams(mc.skinCluster(self.name, q=True, inf=True)) or []

    @property
    def weights(self):
        weights = {}
        for i in self.geometry.get_component_indexes():
            weights[i] = wdt.WeightsDict()
            for jnt, _ in enumerate(self.influences()):
                weights[i][jnt] = self.weightList[i].weights[jnt].value
        return weights

    @weights.setter
    def weights(self, weights):
        for vtx in weights:
            for jnt in weights[vtx]:
                self.weightList[vtx].weights[jnt].value = weights[vtx][jnt]

    @property
    def dq_weights(self):
        dq_weights = wdt.WeightsDict()
        for i, comp in enumerate(mc.ls('{}.weightList[*]'.format(self.name))):
            weight = self.blendWeights[i].value
            if weight:
                dq_weights[i] = weight
        return dq_weights

    @dq_weights.setter
    def dq_weights(self, data):
        data = wdt.WeightsDict(data)
        for vtx in data:
            self.blendWeights[vtx].value = data[vtx]
        for i, vtx in enumerate(mc.ls('{}.weightList[*]'.format(self))):
            if i not in data:
                self.blendWeights[i].value = 0

    def reskin(self):
        for inf in self.influences():
            conns = mc.listConnections(inf.worldMatrix, type='skinCluster', p=True)
            for conn in conns:
                bpm = conn.replace('matrix', 'bindPreMatrix')
                wim = inf.worldInverseMatrix.value
                if not mc.listConnections(bpm):
                    mc.setAttr(bpm, *wim, type='matrix')
                else:
                    print('{} is connected'.format(bpm))
        mc.skinCluster(self, e=True, rbm=True)

    @staticmethod
    def get_skinCluster(obj):
        skn = mel.eval('findRelatedSkinCluster ' + obj)
        return yam(skn) if skn else None


class BlendShape(GeometryFilter):
    def __init__(self, mObject):
        super(BlendShape, self).__init__(mObject)
        self._targets = []
        self._targets_names = {}
        self.get_targets()

    def get_targets(self):
        targets = mc.blendShape(self, q=True, target=True)
        self._targets = [BlendshapeTarget(self, n, i) for i, n in enumerate(targets)]
        self._targets_names = {target.name: target for target in self._targets}
        return self._targets

    def targets(self, target):
        if isinstance(target, int):
            return self._targets[target]
        elif isinstance(target, basestring):
            return self._targets_names[target]
        else:
            raise KeyError(target)

    def weights_attr(self, index):
        return self.inputTarget[0].baseWeights[index]

    @property
    def weights(self):
        weights = wdt.WeightsDict()
        for c, _ in enumerate(self.geometry.get_components()):
            weights[c] = self.weights_attr(c).value
        return weights

    @weights.setter
    def weights(self, weights):
        for i, weight in weights.items():
            self.weights_attr(i).value = weight


class BlendshapeTarget(object):
    def __init__(self, node, name, index):
        self._name = name
        self._node = node
        self._index = index

    def __str__(self):
        return self._name

    def __repr__(self):
        return 'Target({}, {}, {})'.format(self._node, self._name, self._index)

    @property
    def name(self):
        return self._name

    @property
    def index(self):
        return self._index

    @property
    def node(self):
        return self._node

    def weights_attr(self, index):
        return self._node.inputTarget[0].inputTargetGroup[self._index].targetWeights[index]

    @property
    def weights(self):
        weights = wdt.WeightsDict()
        for c, _ in enumerate(self._node.geometry.get_components()):
            weights[c] = self.weights_attr(c).value
        return weights

    @weights.setter
    def weights(self, weights):
        for i, weight in weights.items():
            self.weights_attr(i).value = weight
