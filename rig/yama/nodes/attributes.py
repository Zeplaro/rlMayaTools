import maya.cmds as mc


class Attribute(object):
    settable_properties = ['value',
                           'defaultValue',
                           'hasMinValue',
                           'minValue',
                           'hasMaxValue',
                           'maxValue',
                           'niceName',
                           'keyable',
                           'channelBox',
                           'hidden',
                           'locked',
                           'enumName',
                           ]

    def __init__(self, parent, attr):
        self.__dict__['_parent'] = parent
        self.__dict__['_attr'] = attr

    def __str__(self):
        return '{}.{}'.format(self._parent, self._attr)

    def __repr__(self):
        return "{}({}, '{}')".format(self.__class__.__name__, self._parent, self._attr)

    def __getattr__(self, item):
        return Attribute(self, item)

    def __setattr__(self, key, value):
        if key in self.settable_properties:
            super(Attribute, self).__setattr__(key, value)
        else:
            Attribute(self, key).value = value

    def __getitem__(self, item):
        return MultiAttribute(self, item)

    def __setitem__(self, key, value):
        MultiAttribute(self, key).value = value

    @property
    def node(self):
        if isinstance(self._parent, Attribute):
            return self._parent.node
        else:
            return self._parent

    def get_full_attribute(self):
        if not isinstance(self._parent, Attribute):
            return '{}'.format(self._attr)
        else:
            return self._parent.get_full_attribute() + '.{}'.format(self._attr)

    @property
    def longName(self):
        return self._attr

    @property
    def niceName(self):
        return mc.attributeQuery(self._attr, node=self.obj, niceName=True)

    @niceName.setter
    def niceName(self, value):
        mc.addAttr(self, e=True, niceName=value)

    @property
    def parent(self):
        return self._parent

    def get_parents(self, attrs_only=False):
        if not isinstance(self._parent, Attribute):
            if not attrs_only:
                return [self._parent]
            else:
                return []
        else:
            return self._parent.get_parents(attrs_only=attrs_only) + [self._parent]
    
    @property
    def type(self):
        return mc.getAttr(self, type=True)

    @property
    def value(self):
        return mc.getAttr(self)

    @value.setter
    def value(self, value):
        mc.setAttr(self, value)

    @property
    def defaultValue(self):
        return mc.addAttr(self, q=True, defaultValue=True)
    
    @defaultValue.setter
    def defaultValue(self, value):
        mc.addAttr(self, e=True, defaultValue=value)

    @property
    def hasMinValue(self):
        return mc.attributeQuery(self.name, node=self.obj, minExists=True)

    @hasMinValue.setter
    def hasMinValue(self, value):
        """
        Maya can only toggle the minValue and can not set it to a certain state, regardless of passing True or False,
         which implies the following way of setting it.
        """
        if not bool(value) == bool(self.hasMinValue):
            mc.addAttr(self, e=True, hasMinValue=value)

    @property
    def minValue(self):
        return mc.attributeQuery(self._attr, node=self.obj, minimum=True)[0]

    @minValue.setter
    def minValue(self, value):
        mc.addAttr(self, e=True, minValue=value)

    @property
    def hasMaxValue(self):
        return mc.attributeQuery(self._attr, node=self.obj, maxExists=True)

    @hasMaxValue.setter
    def hasMaxValue(self, value):
        """
        Maya can only toggle the maxValue and can not set it to a certain state, regardless of passing True or False,
         which implies the following way of setting it.
        """
        if not bool(value) == bool(self.hasMaxValue):
            mc.addAttr(self, e=True, hasMaxValue=value)

    @property
    def maxValue(self):
        return mc.attributeQuery(self._attr, node=self.obj, maximum=True)[0]

    @maxValue.setter
    def maxValue(self, value):
        mc.addAttr(self, e=True, maxValue=value)

    @property
    def locked(self):
        return mc.getAttr(self, lock=True)

    @locked.setter
    def locked(self, value):
        mc.setAttr(self, lock=value)

    @property
    def keyable(self):
        return mc.getAttr(self, keyable=True)

    @keyable.setter
    def keyable(self, value):
        mc.setAttr(self, keyable=value)

    @property
    def channelBox(self):
        if not self.keyable and mc.getAttr(channelBox=True):
            return True
        return False

    @channelBox.setter
    def channelBox(self, value):
        if value:
            mc.setAttr(self, keyable=False)
            mc.setAttr(self, channelBox=True)
        else:
            mc.setAttr(self, keyable=False)
            mc.setAttr(self, channelBox=False)

    @property
    def hidden(self):
        if mc.getAttr(self, keyable=True) or mc.getAttr(self, channelBox=True):
            return False
        return True

    @hidden.setter
    def hidden(self, value):
        if value:
            self.channelBox = True
        else:
            mc.setAttr(self, keyable=False)
            mc.setAttr(self, channelBox=False)


class MultiAttribute(Attribute):
    def __init__(self, parent, index):
        super(MultiAttribute, self).__init__(parent, '[{}]'.format(index))
        self.__dict__['_index'] = index

    def __str__(self):
        return '{}[{}]'.format(self._parent, self._index)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self._parent, self._index)

    @property
    def index(self):
        return self._index

    def get_full_attribute(self):
        return self._parent.get_full_attribute() + '{}'.format(self._attr)
