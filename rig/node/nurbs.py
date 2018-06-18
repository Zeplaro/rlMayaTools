import maya.cmds as mc
import node.shape as shp


class Nurbs(shp.Shape):
    def __init__(self, obj):
        super(Nurbs, self).__init__(obj)

    @property
    def cvs(self):
        return mc.ls('{}.cv[:]'.format(self.name), flatten=True)

    @property
    def cps(self):
        cps = mc.ls('{}.cp[:]'.format(self.name), flatten=True)
        cps = [x.replace('.cv', '.cp') for x in cps]
        return cps

    @staticmethod
    def get_control_position(controls):
        return [mc.xform(x, q=True, os=True, t=True) for x in controls]

    @staticmethod
    def set_control_position(controls, positions):
        [mc.xform(control, os=True, t=position) for control in controls for position in positions]


class NurbsCurve(Nurbs):
    def __init__(self, crv):
        super(Nurbs, self).__init__(crv)

    def __len__(self):
        return self['spans'] + self['degree']

    @property
    def arclen(self):
        return mc.arclen(self.name)

    @property
    def data(self):
        data = {'name': self.name,
                'type': self.type,
                'spans': self['spans'],
                'form': self['form'],
                'degree': self['degree'],
                'cps': self.get_control_position(self.cps),
                'knots': self.knots
                }
        return data

    @data.setter
    def data(self, data):
        for datum in data:
            setattr(datum, data[datum])

    @property
    def knots(self):
        nb_knots = len(self) + self['degree'] - 1
        print('Nb of knots: {}'.format(nb_knots))

        if self['form'] == 0:
            knots = range(nb_knots-(self['degree']-1)*2)
            for i in range(self['degree']-1):
                knots = knots[:1] + knots
                knots += knots[-1:]
        else:
            knots = range(nb_knots-(self['degree']-1))
            for i in range(self['degree']-1):
                knots.insert(0, knots[0]-1)

        if self.type == 'bezierCurve':
            knots = []
            for i in range(nb_knots/3):
                for j in range(3):
                    knots.append(i)
        knots = [float(x) for x in knots]
        return knots
