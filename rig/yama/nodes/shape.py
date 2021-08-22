import maya.cmds as mc
import dependNode as dpn


class Shape(dpn.DependNode):
    def __init__(self, name):
        super(Shape, self).__init__(name)
        if 'shape' not in self._type_inheritance:
            raise Exception("{} is not a shape".format(name))

    def get_components(self):
        raise NotImplementedError

    def __len__(self):
        return len(self.get_components())


class Mesh(Shape):
    def __init__(self, name):
        super(Mesh, self).__init__(name)
        if 'mesh' not in self._type_inheritance:
            raise Exception("{} is not a mesh".format(name))

    def get_components(self):
        return mc.ls(self.name + '.vtx[*]', fl=True)

    def get_component_indexes(self):
        for i in range(len(self)):
            yield i


class NurbsCurve(Shape):
    def __init__(self, name):
        super(NurbsCurve, self).__init__(name)
        if 'nurbsCurve' not in self._type_inheritance:
            raise Exception("{} is not a nurbsCurve".format(name))

    def __len__(self):
        return self.spans.value + self.degree.value

    def get_components(self):
        return mc.ls(self.name + '.cv[*]', fl=True)

    def get_component_indexes(self):
        for i in range(len(self)):
            yield i

    @property
    def cps(self):
        cps = mc.ls('{}.cp[:]'.format(self.name), flatten=True)
        cps = [x.replace('.cv', '.cp') for x in cps]
        return cps

    @staticmethod
    def get_control_point_position(controls):
        return [mc.xform(x, q=True, os=True, t=True) for x in controls]

    @staticmethod
    def set_control_point_position(controls, positions):
        [mc.xform(control, os=True, t=position) for control in controls for position in positions]

    @property
    def arclen(self):
        return mc.arclen(self.name)

    @property
    def data(self):
        # todo: copied form old node work, needs cleanup
        data = {'name': self.name,
                'type': self.type,
                'spans': self.spans.value,
                'form': self.form.value,
                'degree': self.degree.value,
                'cps': self.get_control_point_position(self.cps),
                'knots': self.knots
                }
        return data

    @data.setter
    def data(self, data):
        # todo: copied form old node work, needs cleanup
        for d in data:
            setattr(d, data[d])

    @property
    def knots(self):
        # todo: copied form old node work, needs cleanup
        nb_knots = len(self) + self.degree.value - 1
        print('Nb of knots: {}'.format(nb_knots))

        if self.form.value == 0:
            knots = list(range(nb_knots-(self.degree.value - 1) * 2))
            for i in range(self.degree.value - 1):
                knots = knots[:1] + knots
                knots += knots[-1:]
        else:
            knots = list(range(nb_knots-(self.degree.value - 1)))
            for i in range(self.degree.value - 1):
                knots.insert(0, knots[0]-1)

        if self.type == 'bezierCurve':
            knots = []
            for i in range(nb_knots/3):
                for j in range(3):
                    knots.append(i)
        knots = [float(x) for x in knots]
        return knots
