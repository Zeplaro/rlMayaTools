import maya.cmds as mc


def get_sym_data(precision=4, axis='x'):
    l_vtxs = mc.ls(sl=True, fl=True)
    if not l_vtxs:
        mc.warning('Nothing selected')
    obj = l_vtxs[0].split('.')[0]

    positions = get_vtxs_positions(obj, precision)
    table = SymTable(axis)
    unfound = l_vtxs[:]
    for l_vtx in l_vtxs:
        l_index = int(l_vtx.split('[')[-1][:-1])
        l_pos = positions[l_index]
        r_pos = mult_list(l_pos, table.axis_mult)
        for vtx in positions:
            if positions[vtx] == r_pos:
                table[l_index] = vtx
                unfound.remove(l_vtx)
                break
    print('Matching point were not found for : {}'.format(unfound))
    return table


def mult_list(list_a, list_b):
    return [x*y for x, y in zip(list_a, list_b)]


def mirror_map(deformer, attr, table):
    # TODO : Average mid vtxs
    for l_vtx in table:
        l_weight = mc.getAttr(deformer+'.'+attr.format(l_vtx))
        mc.setAttr(deformer+'.'+attr.format(table[l_vtx]), l_weight)


def flip_map(deformer, attr, table):
    for l_vtx in table:
        r_vtx = table[l_vtx]
        l_weight = mc.getAttr(deformer+'.'+attr.format(l_vtx))
        r_weight = mc.getAttr(deformer+'.'+attr.format(r_vtx))
        mc.setAttr(deformer+'.'+attr.format(table[l_vtx]), r_weight)
        mc.setAttr(deformer+'.'+attr.format(table[r_vtx]), l_weight)


def mirror_pos(obj, table):
    for l_vtx in table:
        l_pos = mc.xform('{}.vtx[{}]'.format(obj, l_vtx), q=True, t=True, os=True)
        r_pos = mult_list(l_pos, table.axis_mult)
        mc.xform('{}.vtx[{}]'.format(obj, table[l_vtx]), t=r_pos, os=True)
    for mid in table.mids:
        mc.xform('{}.vtx[{}]'.format(obj, mid), t=0.0, os=True)


def flip_pos(obj, table):
    for l_vtx in table:
        l_pos = mc.xform('{}.vtx[{}]'.format(obj, l_vtx), q=True, t=True, os=True)
        r_pos = mc.xform('{}.vtx[{}]'.format(obj, table[l_vtx]), q=True, t=True, os=True)

        mc.xform('{}.vtx[{}]'.format(obj, l_vtx), t=r_pos, os=True)
        mc.xform('{}.vtx[{}]'.format(obj, table[l_vtx]), t=l_pos, os=True)

    for mid in table.mids:
        pos = mc.xform('{}.vtx[{}]'.format(obj, mid), q=True, t=True, os=True)
        pos = mult_list(pos, table.axis_mult)
        mc.xform('{}.vtx[{}]'.format(obj, mid), t=pos, os=True)


def get_vtxs_positions(obj, precision=4):
    vtxs = mc.ls(obj+'.vtx[*]', fl=True)
    positions = {}
    for vtx in vtxs:
        index = int(vtx.split('[')[-1][:-1])
        pos = mc.xform(vtx, q=True, t=True, os=True)
        positions[index] = [round(x, precision) for x in pos]
    return positions


class SymTable(dict):
    def __init__(self, axis='x', precision=4):
        super(SymTable, self).__init__()
        self.axis = axis
        self.axis_mult = [1, 1, 1]
        self.axis_mult[('x', 'y', 'z').index(axis)] *= -1
        self.mids = []
