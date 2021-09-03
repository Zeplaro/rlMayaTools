# encoding: utf8

from maya import cmds


# todo : LOOK INTO MRichSelection.getSymmetry()
# todo : https://stackoverflow.com/questions/44702826/maya-api-python-symmetry-table-with-mrichselection


obj = 'ori'
precision = 4
l_vtxs = cmds.ls(sl=True, fl=True)

vtxs = cmds.ls('ori.vtx[*]', fl=True)
positions = {i: [round(y, precision) for y in cmds.xform(x, q=True, t=True, os=True)] for i, x in enumerate(vtxs)}

sym_map = {}

for l_vtx in l_vtxs:
    index = int(l_vtx.split('[')[-1][:-1])
    pos = positions[index]
    mir_pos = [pos[0] * -1, pos[1], pos[2]]
    for vtx, position in positions.items():
       if position == mir_pos:
          print(l_vtx, index, vtx)
          sym_map[index] = vtx
       break
# TODO : check if some are missing in the sym table
print(len(l_vtxs), len(sym_map))
for i in l_vtxs:
    index = int(i.split('[')[-1][:-1])
    if index not in sym_map:
       print('{} not in sym table'.format(i))


# CLUSTERS
for l_index, r_index in sym_map.items():
    l_weight = cmds.getAttr('testclust.weightList[0].weights[{}]'.format(l_index))
    r_weight = cmds.getAttr('testclust.weightList[0].weights[{}]'.format(r_index))

    cmds.setAttr('testclust.weightList[0].weights[{}]'.format(l_index), r_weight)
    cmds.setAttr('testclust.weightList[0].weights[{}]'.format(r_index), l_weight)


# Blendshapes targets flip
target_index = 10
for l_index, r_index in sym_map.items():
 l_weight = cmds.getAttr('testbsh.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]'.format(target_index, l_index))
 r_weight = cmds.getAttr('testbsh.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]'.format(target_index, r_index))

 cmds.setAttr('testbsh.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]'.format(target_index, l_index), r_weight)
 cmds.setAttr('testbsh.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]'.format(target_index, r_index), l_weight)

# Blendshapes base weights sym
for l_index, r_index in sym_map.items():
 l_weight = cmds.getAttr('blendShape100.inputTarget[0].baseWeights[{}]'.format(l_index))
 cmds.setAttr('blendShape100.inputTarget[0].baseWeights[{}]'.format(r_index), l_weight)

# blendshape normalize
targets = 10, 11
for index, _ in enumerate(vtxs):
 weight_a = cmds.getAttr('BS_MOUTH_01_C.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]'.format(targets[0], index))
 weight_b = cmds.getAttr('BS_MOUTH_01_C.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]'.format(targets[1], index))
 factor = 1.0/(weight_a+weight_b)

 cmds.setAttr('BS_MOUTH_01_C.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]'.format(targets[0], index), weight_a * factor)
 cmds.setAttr('BS_MOUTH_01_C.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]'.format(targets[1], index), weight_b * factor)


# Flip shape
obj = cmds.ls(sl=True)[0]
for l_index, r_index in sym_map.items():
 l_pos = cmds.xform('{}.vtx[{}]'.format(obj, l_index), q=True, t=True, os=True)
 r_pos = cmds.xform('{}.vtx[{}]'.format(obj, r_index), q=True, t=True, os=True)
 new_l_pos = -r_pos[0], r_pos[1], r_pos[2]
 new_r_pos = -l_pos[0], l_pos[1], l_pos[2]

 cmds.xform('{}.vtx[{}]'.format(obj, l_index), t=new_l_pos, os=True)
 cmds.xform('{}.vtx[{}]'.format(obj, r_index), t=new_r_pos, os=True)





import yama.mapmixer as mm
t = mm.get_sym_data()
# Blendshapes targets mirror
target_index = 1
for l, r in t.items():
    l_weight = cmds.getAttr(
    'FACE_BodyClothed_GeoShape_BS.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]'.format(target_index, l))
    cmds.setAttr(
    'FACE_BodyClothed_GeoShape_BS.inputTarget[0].inputTargetGroup[{}].targetWeights[{}]'.format(target_index, r),
    l_weight)

# Deltamush mirror
for r, l in t.items():
    l_weight = cmds.getAttr('deltaMush1.weightList[0].weights[{}]'.format(l))
    cmds.setAttr('deltaMush1.weightList[0].weights[{}]'.format(r), l_weight)