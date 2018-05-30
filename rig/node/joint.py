import maya.cmds as mc
import node.transform as transform


class Joint(transform.Transform):
    def __init__(self, obj):
        super(Joint, self).__init__(obj)
