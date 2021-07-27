import maya.cmds as mc
import deformer as dfn
import depend as dpn
import weightsdict as wdt


class GeometryFilter(dpn.Depend):
    def __init__(self, node):
        print('geof')
        super(GeometryFilter, self).__init__(node)
        if 'geometryFilter' not in self._type_inheritance:
            raise Exception("{} is not a geometryFilter".format(node))

    @property
    def geometry(self):
        geo = mc.deformer(self.name, q=True, geometry=True)
        return dfn.node_to_class(geo[0]) if geo else None


class WeightGeometryFilter(GeometryFilter):
    def __init__(self, node):
        super(WeightGeometryFilter, self).__init__(node)
        if 'weightGeometryFilter' not in self._type_inheritance:
            raise Exception("{} is not a weightGeometryFilter".format(node))

    @property
    def weights(self):
        weights = DeformerWeights(self)
        for c, _ in enumerate(self.geometry.get_components()):
            weights[c] = mc.getAttr('{}.weightList[0].weights[{}]'.format(self, c))
        return weights

    @weights.setter
    def weights(self, weights):
        for i, weight in weights.items():
            mc.setAttr('{}.weightList[0].weights[{}]'.format(self, i), weight)


class DeformerWeights(wdt.WeightsDict):
    def __init__(self, node):
        super(DeformerWeights, self).__init__()
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
        weights = super(DeformerWeights, self).__invert__()
        self.apply_weights(weights)

    def apply_weights(self, weights=None):
        if weights is None:
            self._node.weights = self
        else:
            self._node.weights = weights

    def clamp(self, min_value=0.0, max_value=1.0):
        super(DeformerWeights, self).clamp(min_value, max_value)
        self.apply_weights()
