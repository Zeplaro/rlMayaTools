# encoding: utf8

import maya.cmds as mc
import geometryFilter as gof

try:
    basestring
except NameError:
    basestring = str


class BlendShape(gof.GeometryFilter):
    def __init__(self, name):
        super(BlendShape, self).__init__(name)
        if 'blendShape' not in self._type_inheritance:
            raise Exception("{} is not a blendShape".format(name))
        self._targets = []
        self._targets_names = {}
        self.get_targets()

    def get_targets(self):
        targets = mc.blendShape(self, q=True, target=True)
        self._targets = [Target(self, n, i) for i, n in enumerate(targets)]
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
        print('getting weights')
        weights = gof.DeformerWeights(self)
        print(weights)
        for c, _ in enumerate(self.geometry.get_components()):
            weights[c] = self.weights_attr(c).value
        return weights

    @weights.setter
    def weights(self, weights):
        for i, weight in weights.items():
            self.weights_attr(i).value = weight


class Target(object):
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
        weights = gof.DeformerWeights(self)
        for c, _ in enumerate(self._node.geometry.get_components()):
            weights[c] = self.weights_attr(c).value
        return weights

    @weights.setter
    def weights(self, weights):
        for i, weight in weights.items():
            self.weights_attr(i).value = weight
