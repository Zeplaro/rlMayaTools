import maya.api.OpenMaya as om


def get_Mplug(plug):
    attrs = plug.split('.')
    node = attrs.pop(0)
    data = []
    for attr in attrs:
        index = None
        if '[' in attr:
            attr, index = attr.split('[')
            index = int(index[:-1])
        data.append((attr, index))
    sel = om.MSelectionList()
    sel.add(node)
    mObject = sel.getDependNode(0)
    dep_node = om.MFnDependencyNode(mObject)
    plug = dep_node.findPlug(data[-1][0], True)
    for attr, index in data:
        sub_plug = dep_node.findPlug(attr, True).attribute()
        if index is not None:
            plug.selectAncestorLogicalIndex(index, sub_plug)
    return plug


def getAttr(plug):
    plug = get_Mplug(plug)

    def get_plug_value(mPlug):
        attr_type = mPlug.attribute().apiTypeStr
        if attr_type in ('kNumericAttribute', ):
            return mPlug.asDouble()
        elif attr_type in ('kDistance', ):
            return mPlug.asMDistance().asUnits(om.MDistance.uiUnit())
        elif attr_type in ('kAngle', ):
            return mPlug.asMAngle().asUnits(om.MAngle.uiUnits())
        elif attr_type in ('kTypedAttribute', ):
            return mPlug.asString()
        elif attr_type in ('kTimeAttribute', ):
            return mPlug.asMTime().asUnits(om.MTime.uiUnits())
        elif attr_type in ('kAttribute2Double', 'kAttribute3Double', 'kAttribute4Double', ):
            values = []
            for child_index in range(mPlug.numChildren()):
                values.append(get_plug_value(mPlug.chid(child_index)))
            return values
        elif attr_type in ('kMatrixAttribute', 'kFloatMatrixAttribute', ):
            data_handle = mPlug.MDataHandle()
            if attr_type == 'kMatrixAttribute':
                return data_handle.asMatrix()
            elif attr_type == 'kFloatMatrixAttribute':
                return data_handle.asFloatMatrix()

    return get_plug_value(plug)


def setAttr(plug, value):
    plug = get_Mplug(plug)

    def set_plug_value(mPlug, plug_value):
        attr_type = mPlug.attribute().apiTypeStr
        if attr_type in ('kNumericAttribute', ):
            mPlug.setDouble(plug_value)
        elif attr_type in ('kDistance', ):
            mPlug.setMDistance(om.MDistance(plug_value, om.MDistance.uiUnit()))
        elif attr_type in ('kAngle', ):
            mPlug.setMAngle(om.MAngle(value, om.MAngle.uiUnits()))
        elif attr_type in ('kTypedAttribute', ):
            mPlug.setString(plug_value)
        elif attr_type in ('kTimeAttribute', ):
            mPlug.setMTime(om.MTime(value, om.MTime.uiUnits()))
        elif attr_type in ('kAttribute2Double', 'kAttribute3Double', 'kAttribute4Double', ):
            for child_index in range(mPlug.numChildren()):
                set_plug_value(mPlug.chid(child_index, value[child_index]))
        elif attr_type in ('kMatrixAttribute', 'kFloatMatrixAttribute', ):
            data_handle = mPlug.MDataHandle()
            if attr_type == 'kMatrixAttribute':
                data_handle.setMMatrix(plug_value)
            elif attr_type == 'kFloatMatrixAttribute':
                data_handle.setMFloatMatrix(plug_value)
            mPlug.setMDataHandle(data_handle)

        set_plug_value(plug, value)
