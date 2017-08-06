import maya.cmds as mc


class DepNodes:

    def __init__(self, obj):
        self.shape = self.get_shape(obj)
        self.skn = self.get_skinCluster(obj)

    def get_shape(self, obj):
        self.shape = mc.listRelatives(obj, s=True, pa=1, ni=True) or []
        return self.shape

    def get_skinCluster(self, obj):
        self.skn = mc.ls(mc.listHistory(obj, ac=True, pdo=True), type='skinCluster')
        return self.skn
