import maya.cmds as mc
import maya.mel as mel
import dependNode as dpn
import geometryFilter as gof
import weightsdict as wdt


def get_skinCluster(obj):
    skn = mel.eval('findRelatedSkinCluster ' + obj)
    return SkinCluster(skn) if skn else None


class SkinCluster(gof.GeometryFilter):
    def __init__(self, name):
        super(SkinCluster, self).__init__(name)
        if 'skinCluster' not in self._type_inheritance:
            raise Exception("{} is not a skinCluster".format(name))
        self._weights_attr = None

    def influences(self):
        return dpn.yams(mc.skinCluster(self.name, q=True, inf=True)) or []

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
