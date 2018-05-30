import maya.cmds as mc
import node.depend as dep
import os
import json


class SkinCluster(dep.Depend):
    def __init__(self, skn):
        super(SkinCluster, self).__init__(skn)

    @property
    def infs(self):
        return mc.skinCluster(self.name, q=True, inf=True)

    @property
    def skin_data(self):
        skin_dict = {
            'name': self.name,
            'skinningMethod': self['skinningMethod'],
            'maximumInfluences': mc.skinCluster(self.name, q=True, mi=True),
            'normalizeWeights': mc.skinCluster(self.name, q=True, nw=True),
            'obeyMaxInfluences': mc.skinCluster(self.name, q=True, omi=True),
            'weightDistribution': mc.skinCluster(self.name, q=True, wd=True),
            'influences': {},
            'weigths': self.weights,
            }
        for i, inf in enumerate(self.infs):
            skin_dict['influences'][i] = {}
            skin_dict['influences'][i]['index'] = i
            skin_dict['influences'][i]['name'] = inf
            skin_dict['influences'][i]['position'] = mc.xform(inf, q=True, ws=True, t=True)
        if skin_dict['skinningMethod'] > 1:
            skin_dict['dq_weigths'] = self.dq_weights
        return skin_dict

    @skin_data.setter
    def skin_data(self, data):
        mc.skinCluster(self.name, e=True,
                       sm=data['skinningMethod'],
                       mi=data['maximumInfluences'],
                       nw=data['normalizeWeights'],
                       omi=data['obeyMaxInfluences'],
                       wd=data['weightDistribution'],
                       )
        self.weights = data['weigths']
        if data['skinningMethod'] > 1:
            self.dq_weights = data['dq_weigths']
            self['dqsSupportNonRigid'] = 1
            self['deformUserNormals'] = 0
        if data['normalizeWeights'] == 1:
            mc.skinCluster(self.name, e=True, nw=True)
            mc.skinCluster(self.name, e=True, forceNormalizeWeights=True)

    @property
    def dq_weights(self):
        dq_weights = {}
        for i, comp in enumerate(mc.ls('{}.weightList[*]'.format(self.name))):
            weight = self['blendWeights[{}]'.format(i)]
            if weight:
                dq_weights[i] = weight
        return dq_weights

    @dq_weights.setter
    def dq_weights(self, data):
        for comp, weight in data.iteritems():
            self['blendWeights[{}]'.format(comp)] = weight
        for i, comp in enumerate(mc.ls('{}.weightList[*]'.format(self.name))):
            if not (i in data or str(i) in data):  # Checking str because json index can only be str
                self['blendWeights[{}]'.format(i)] = 0

    @property
    def weights(self):
        weight_dict = {}
        for i, comp in enumerate(mc.ls('{}.weightList[*]'.format(self.name))):
            weight_dict[i] = {}
            for j, jnt in enumerate(self.infs):
                weight = self['weightList[{}]weights[{}]'.format(i, j)]
                if weight:
                    weight_dict[i][j] = weight
        return weight_dict

    @weights.setter
    def weights(self, data):
        for comp, infs in data.iteritems():
            for inf, weight in infs.iteritems():
                self['weightList[{}]weights[{}]'.format(comp, inf)] = weight
            for inf_index, _ in enumerate(self.infs):
                if not (inf_index in infs or str(inf_index) in infs):  # Checking str because json index can only be str
                    self['weightList[{}]weights[{}]'.format(comp, inf_index)] = 0

    @staticmethod
    def load_skin_file(path, file_name):
        full_path = os.path.join(path, file_name)
        with open(full_path, 'r') as skinFile:
            data = json.load(skinFile)
        print(data)
        return data

    def save_skin_file(self, path, file_name):
        full_path = os.path.join(path, file_name)
        with open(full_path, 'w') as skinFile:
            json.dump(self.skin_data, skinFile, indent=2)

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
