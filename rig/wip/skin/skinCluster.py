import maya.cmds as mc
import tbx
import json
import os

# todo : setting deform user normal to 0 if weight blended dQ

def get_skin(obj=None):
    if not obj:
        obj = mc.ls(sl=True, fl=True, long=True)
    if not obj:
        return 'No object'
    else:
        obj = obj[0]

    obj = skinCluster(obj)

    return obj.skinDict


class skinCluster:

    def __init__(self, obj):
        self.name = self.get_skinCluster(obj)
        if self.name:
            self.infs = self.get_infs()
            self.skinDict = self.get_skinDict()
        else:
            print('No skinCluster')
            self.infs = []
            self.skinDict = {}

    def get_infs(self):
        sel = mc.ls(sl=True)
        print(self.name)
        mc.select(mc.skinCluster(self.name, q=True, inf=True))
        infs = mc.ls(sl=True, fl=True, long=True)
        mc.select(sel)
        return infs

    def get_jnt_weights(self, jntIndex):
        weights = [mc.getAttr('{}.weightList[{}]weights[{}]'.format(self.name, j, jntIndex))
                   for j, vtx in enumerate(self.vtxs)]
        return weights

    def get_dQ_weights(self):
        dQWeights = {}
        for i, vtx in enumerate(self.vtxs):
            dQWeight = mc.getAttr('{}.blendWeights[{}]'.format(self.name, i))
            if dQWeight:
                dQWeights[i] = dQWeight
        return dQWeights

    @staticmethod
    def get_inf_pos(inf):
        return mc.xform(inf, q=True, ws=True, t=True)

    def get_skinDict(self):
        self.skinDict = {}
        if not self.name:
            return 'No skinCluster'
        self.skinDict['skinClusterInfo'] = {}
        self.skinDict['skinClusterInfo']['Name'] = self.name
        self.skinDict['skinClusterInfo']['skinMethod'] = mc.skinCluster(self.name, q=True, sm=True)
        self.skinDict['skinClusterInfo']['maximumInfluences'] = mc.skinCluster(self.name, q=True, mi=True)
        self.skinDict['skinClusterInfo']['normalizeWeights'] = mc.skinCluster(self.name, q=True, nw=True)
        self.skinDict['skinClusterInfo']['obeyMaxInfluences'] = mc.skinCluster(self.name, q=True, omi=True)
        self.skinDict['skinClusterInfo']['weightDistribution'] = mc.skinCluster(self.name, q=True, wd=True)
        for i, inf in enumerate(self.infs):
            self.skinDict[i] = {}
            self.skinDict[i]['index'] = i
            self.skinDict[i]['name'] = inf
            self.skinDict[i]['position'] = self.get_inf_pos(inf)
            self.skinDict[i]['weights'] = self.get_jnt_weights(i)
        self.skinDict['dQWeigths'] = self.get_dQ_weights()

        return self.skinDict

    def apply_skinDict(self):
        for i, inf in enumerate(self.infs):
            print('Setting {}'.format(inf.split('|')[-1]))
            for j, vtx in enumerate(self.vtxs):
                print('    Setting {}'.format(vtx.split('|')[-1]))
                weight = self.skinDict[i]['weights'][j]
                mc.setAttr('{}.weightList[{}]weights[{}]'.format(self.name, j, i), weight)
        print('Setting dQ')
        for i, vtx in enumerate(self.vtxs):
            weight = self.skinDict['dQWeigths'][i]
            mc.setAttr('{}.blendWeights[{}]'.format(self.name, i), weight)
        print('Done')

    def save_skin(self, path, fileName):
        fullPath = os.path.join(path, fileName)
        with open(fullPath, 'w') as skinFile:
            json.dump(self.skinDict, skinFile, indent=2)
        return fullPath

    @staticmethod
    def load_skinFile(path, fileName):
        fullPath = os.path.join(path, fileName)
        with open(fullPath, 'r') as skinFile:
            dict = json.load(skinFile)
        return dict

    def apply_skinFile(self, path, fileName):
        skinFile = self.load_skinFile('', '')
        self.skinDict = skinFile
        self.apply_skinDict()
        return self.skinDict
