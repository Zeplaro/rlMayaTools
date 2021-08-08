import maya.cmds as mc
import deformer as dfn
import depend as dpn
import weightsdict as wdt


class GeometryFilter(dpn.Depend):
    def __init__(self, name):
        super(GeometryFilter, self).__init__(name)
        if 'geometryFilter' not in self._type_inheritance:
            raise Exception("{} is not a geometryFilter".format(name))

    @property
    def geometry(self):
        geo = mc.deformer(self.name, q=True, geometry=True)
        return dfn.node_to_class(geo[0]) if geo else None


class WeightGeometryFilter(GeometryFilter):
    def __init__(self, name):
        super(WeightGeometryFilter, self).__init__(name)
        if 'weightGeometryFilter' not in self._type_inheritance:
            raise Exception("{} is not a weightGeometryFilter".format(name))

    @property
    def weights(self):
        weights = DeformerWeights(self)
        for i in self.geometry.get_components_index():
            weights[i] = self.weights_attr(i).value
        return weights

    @weights.setter
    def weights(self, weights):
        for i, weight in weights.items():
            self.weights_attr(i).value = weight

    def weights_attr(self, index):
        return self.attr.weightList[0].weights[index]


class DeformerWeights(wdt.WeightsDict):
    def __init__(self, node):
        print('trying init DW')
        super(DeformerWeights, self).__init__()
        print('init DW')
        self._node = node

    def __iadd__(self, other):
        super(DeformerWeights, self).__iadd__(other)
        self.apply_weights()

    def __isub__(self, other):
        super(DeformerWeights, self).__isub__(other)
        self.apply_weights()

    def __imul__(self, other):
        super(DeformerWeights, self).__imul__(other)
        self.apply_weights()

    def __idiv__(self, other):
        super(DeformerWeights, self).__idiv__(other)
        self.apply_weights()

    def invert(self):
        self._node.weights = super(DeformerWeights, self).__invert__()

    def apply_weights(self):
        self._node.weights = self

    def clamp(self, min_value=0.0, max_value=1.0):
        super(DeformerWeights, self).clamp(min_value, max_value)
        self.apply_weights()


def normalize_weights(*weights):
    if any((not isinstance(x, DeformerWeights) for x in weights)):
        weights_types = [type(x).__name__ for x in weights]
        raise ValueError('geometryFilter.normalize_weights() expects DeformerWeights objects and was given: {}'.format(weights_types))
    new_weights = wdt.normalize_weights(*weights)
    for w, nw in zip(weights, new_weights):
        w.replace_weights(nw)
        w.apply_weights()
