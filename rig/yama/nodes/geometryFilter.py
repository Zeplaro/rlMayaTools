import maya.cmds as mc
import deformer as dfn
import depend as dpn
import weightdict as wdt


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
        weights = wdt.WeightsDict()
        for c, _ in enumerate(self.geometry.get_components()):
            weights[c] = mc.getAttr('{}.weightList[0].weights[{}]'.format(self, c))
        return weights

    @weights.setter
    def weights(self, weights):
        for i, weight in weights.items():
            mc.setAttr('{}.weightList[0].weights[{}]'.format(self, i), weight)
