import maya.cmds as mc


def do_shapeMirror():
    for ctrl in mc.ls(sl=1):
        nspace=ctrl.split(':')
        name=nspace[-1]
        if len(nspace)>1:
            nspace.pop(-1)
            nspace=':'.join(nspace)
            nspace+=':'
        else:
            nspace=''
        if name.startswith('L_'):
            master=ctrl
            slave=nspace+name.replace('L_','R_',1)
        elif name.startswith('R_'):
            master=ctrl
            slave=nspace+name.replace('R_','L_',1)
        else:
            continue
        if not mc.objExists(slave):
            continue

        if mc.objectType(ctrl, isType='nurbsCurve') or mc.objectType(ctrl, isType='nurbsSurface'):
            shM=[master]
            shS=[slave]
        elif mc.objectType(ctrl, isType='transform'):
            shM=mc.listRelatives(master,c=1,s=1,pa=1)
            shS=mc.listRelatives(slave,c=1,s=1,pa=1)
        else:
            continue
        if (shM is None) or (shS is None):
            continue

        for shape in shM:
            cvs = mc.getAttr(shape+'.cp', s=1)
            for cv in range(cvs):
                mc.move(0.1,0.1,0.1,shape+'.cp['+str(cv)+']',r=1)
    print('__DONE__')