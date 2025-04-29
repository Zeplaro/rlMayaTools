# encoding: utf8

# import numpy as np
from maya import cmds

import yama as ym


def shapesFromSelection():
    shapes = ym.YamList()
    for i in ym.selected():
        if i.isa("transform"):
            shapes += i.shapes(type="nurbsCurve")
        elif i.isa("nurbsCurve"):
            shapes.append(i)
    return shapes


class Mirror:
    @staticmethod
    def matrix_maya_to_row(matrix):
        matrix = [round(x, 3) for x in matrix]
        return [matrix[0:4], matrix[4:8], matrix[8:12], matrix[12:16]]

    @classmethod
    def compare_to_world(cls, matrix):
        if len(matrix) > 3:
            matrix.pop(-1)
            for row in matrix:
                row.pop(-1)
        world = [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]
        result = cls.matmul(world, matrix)
        table = []
        for row in result:
            max_value = max(row, key=abs)
            axis = "xyz"[list(row).index(max_value)]
            if max_value < 0:
                axis = "-" + axis
            table.append(axis)
        return table

    @classmethod
    def get_mirror_table(cls, left, right, axis="x"):
        left = cls.compare_to_world(
            cls.matrix_maya_to_row(left.getXform(m=True, ws=True))
        )
        right = cls.compare_to_world(
            cls.matrix_maya_to_row(right.getXform(m=True, ws=True))
        )
        table = []
        for l_axis, r_axis in zip(left, right):
            if l_axis == r_axis:
                value = 1
            else:
                value = -1
            if l_axis[-1] == axis:
                value *= -1
            table.append(value)
        return table

    @staticmethod
    def matmul(a, b):
      rows_a = len(a)
      cols_a = len(a[0])
      rows_b = len(b)
      cols_b = len(b[0])

      if cols_a != rows_b:
        raise ValueError("Matrices are not compatible for multiplication")

      result = [[0 for _ in range(cols_b)] for _ in range(rows_a)]

      for i in range(rows_a):
        for j in range(cols_b):
          for k in range(cols_a):
            result[i][j] += a[i][k] * b[k][j]

      return result

    @classmethod
    def mirror(cls, left, axis="x"):
        left = ym.yam(left)
        right = cls.findMirror(left)
        if not right:
            return
        table = cls.get_mirror_table(left, right, axis=axis)
        for l_shape, r_shape in zip(left.shapes(), right.shapes()):
            for pose, r_cv in zip(l_shape.cv.getPositions(), r_shape.cv):
                new_pose = [x * mult for x, mult in zip(pose, table)]
                r_cv.setPosition(new_pose, ws=False)

    @staticmethod
    def findMirror(ctrl):
        mirror_ctrl = ""
        if ctrl.name.startswith("l_"):
            mirror_ctrl = "r_" + ctrl.name[2:]
        elif ctrl.name.startswith("r_"):
            mirror_ctrl = "l_" + ctrl.name[2:]
        elif ":" in ctrl.name:
            split = ctrl.name.split(":")
            if split[-1].startswith("l_"):
                split[-1] = "r_" + split[-1][2:]
                mirror_ctrl = ":".join(split)
            elif split[-1].startswith("r_"):
                split[-1] = "r_" + split[-1][2:]
                mirror_ctrl = ":".join(split)

        if not cmds.objExists(mirror_ctrl):
            print(f"No mirror ctrl of '{ctrl}' found")
            return
        return ym.yam(mirror_ctrl)

    @classmethod
    def mirror_selected(cls):
        sel = ym.selected()
        print(f"Mirroring {len(sel)} objects")
        for i in sel:
            cls.mirror(i)
        print("Done")


def copyShapes(ws=False):
    source, *targets = ym.selected()
    if source.isa("transform"):
        source = source.shapes(type="nurbsCurve")
    elif source.isa("nurbsCurve"):
        source = [source]
    else:
        return

    target_shapes = []
    for target in targets:
        if target.isa("nurbsCurve"):
            target_shapes.append([target])
        elif target.isa("transform"):
            target_shapes.append(target.shapes(type="nurbsCurve"))

    source_positions = [shape.cv.getPositions(ws=ws) for shape in source]
    for target in target_shapes:
        for source_pos, target_shape in zip(source_positions, target):
            target_shape.cv.setPositions(source_pos, ws=ws)


def selectShapes():
    shapes = shapesFromSelection()
    ym.select(shapes)
    print(f"Selected : {shapes.names}")


def selectIntermediateShapes():
    shapes = ym.YamList(x.intermediateShapes(type="nurbsCurve") for x in ym.selected() if x.isa("transform"))
    ym.select(*shapes)
    print(f"Selected : {shapes}")


def selectCvs():
    cvs = [shape.cv for shape in shapesFromSelection()]
    ym.select(*cvs)


def parentShapes():
    cmds.parent(r=True, s=True)


def indexColor(index, on_transform):
    objs = set()
    if on_transform:
        for i in ym.selected():
            if i.isa("transform"):
                objs.add(i)
            elif i.isa("shape"):
                objs.add(i.parent)
    else:
        objs = shapesFromSelection()

    for obj in objs:
        obj.overrideEnabled.value = True
        obj.overrideRGBColors.value = False
        obj.overrideColor.value = index


def rgbColor():
    # TODO
    ...


def copyColor(on_transform):
    source, *objs = ym.selected()

    if source.isa("transform"):
        source = source.shape
    while True:
        if source.overrideEnabled.value:
            break
        if not source.parent:
            source = None
            break
        source = source.parent

    targets = []
    if on_transform:
        for i in objs:
            if i.isa("transform"):
                targets.add(i)
            elif i.isa("shape"):
                targets.add(i.parent)
    else:
        targets = shapesFromSelection()

    if not source:
        for target in targets:
            while target:
                target.overrideEnabled.value = False
                target = target.parent

    else:
        rgb = source.overrideRGBColors.value
        index = source.overrideColor.value
        rgb_color = source.overrideColorRGB.value
        for target in targets:
            target.overrideEnabled.value = True
            target.overrideRGBColors.value = rgb
            target.overrideColor.value = index
            target.overrideColorRGB.value = rgb_color


def setDrawingOverride(value):
    for i in ym.selected():
        i.overrideEnabled.value = value
