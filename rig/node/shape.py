import maya.cmds as mc
import node.dag as dag


class Shape(dag.Dag):
    def __init__(self, obj):
        super(Shape, self).__init__(obj)
        print('shape init!!!!')

    @property
    def skinCluster(self):
        skn = mc.ls(mc.listHistory(self.name, ac=True, pdo=True), type='skinCluster')
        if skn:
            return skn.SkinCluster(skn[0])
        else:
            return None

    @property
    def parent(self):
        return mc.listRelatives(self.name, p=True, fullPath=True)

    @parent.setter
    def parent(self, parent):
        mc.parent(self.name, parent, r=True, s=True)
