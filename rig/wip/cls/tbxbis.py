import maya.cmds as mc

class dep_nodes:

    def __init__(self, obj):
        self.shape = [shape for shape in mc.listRelatives(obj, s=True, pa=1) or [] if 'Orig' not in shape]
        self.skn = mc.ls(mc.listHistory(obj, ac=True, pdo=True), type='skinCluster')

    def get_shape(self, obj):
        self.shape = [shape for shape in mc.listRelatives(obj, s=True, pa=1) or [] if 'Orig' not in shape]
        return self.shape

    def get_sknCluster(self, obj):
        self.skn = mc.ls(mc.listHistory(obj, ac=True, pdo=True), type='skinCluster')
        return self.skn
