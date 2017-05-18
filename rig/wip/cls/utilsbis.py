import maya.cmds as mc


class utils:

    def get_shape(self):
        shapes = []
        [shapes.append(shape) for shape in mc.listRelatives(self, s=True, pa=1) or [] if 'Orig' not in shape]
        return shapes
