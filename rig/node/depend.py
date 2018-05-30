import maya.cmds as mc


class Depend(object):
    def __init__(self, obj):
        self._name = obj

    def __repr__(self):
        return self.name

    def __getitem__(self, keys):
        solo = False
        if isinstance(keys, basestring):
            keys = [keys]
            solo = True
        values = []
        keys = keys
        for key in keys:
            values.append(mc.getAttr('{}.{}'.format(self.name, key)))
        if solo:
            values = values[0]
        else:
            values = tuple(values)
        return values

    def __setitem__(self, keys, values):
        if isinstance(keys, basestring):
            keys = [keys]
            values = [values]
        for key, value in zip(keys, values):
            mc.setAttr('{}.{}'.format(self.name, key), value)

    def __bool__(self):
        return mc.objExists(self.name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        name = mc.rename(self.name, new_name)
        self._name = name

    @property
    def type(self):
        return mc.nodeType(self.name)


