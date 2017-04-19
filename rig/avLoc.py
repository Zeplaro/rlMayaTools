import maya.cmds as mc


def do_avLoc():

    vtxs = [x for x in mc.ls(sl=True, fl=True) if '.vtx[' in x] or []
    ess = [x for x in mc.ls(sl=True, fl=True) if '.e[' in x] or []
    fs = [x for x in mc.ls(sl=True, fl=True) if '.f[' in x] or []
    if not ess and not vtxs and not fs:
        mc.warning('Please select vertexes, edges or faces')
        return 'Please select vertexes, edges or faces'

    pos = []
    # Vertexes
    for vtx in vtxs:
        pos.append(mc.xform(vtx, q=1, ws=1, t=1))
    # Edges
    for es in ess:
        esvtxs = mc.xform(es, q=1, ws=1, t=1)
        pos.append(esvtxs[0:3])
        pos.append(esvtxs[3:6])
    # Faces
    for f in fs:
        esvtxs = mc.xform(f, q=1, ws=1, t=1)
        pos.append(esvtxs[0:3])
        pos.append(esvtxs[3:6])
        pos.append(esvtxs[6:9])
        pos.append(esvtxs[9:12])

    posx = []
    posy = []
    posz = []
    for each in pos:
        posx.append(each[0])
        posy.append(each[1])
        posz.append(each[2])
    av = [(min(posx)+max(posx))/2, (min(posy)+max(posy))/2, (min(posz)+max(posz))/2]
    loc = mc.spaceLocator(n='avLoc#')
    mc.xform(loc, ws=1, t=av)
    return loc
