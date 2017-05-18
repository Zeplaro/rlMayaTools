import maya.cmds as mc


class utils:
    def __init__(self, obj, shape):

        self.shape = [shape for shape in mc.listRelatives(obj, s=True, pa=1) or [] if 'Orig' not in shape]
