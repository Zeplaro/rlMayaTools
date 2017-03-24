import maya.cmds as mc


def do_shapeMirror(axis='x',space='ws'):
    if axis=='z':
        axis=2
    elif axis=='y':
        axis=1
    else:
        axis=0
    if space=='os':
        space='os'
    else:
        space='ws'

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
            mc.warning('No side found on '+ctrl+'!')
            continue
        if not mc.objExists(slave):
            mc.warning(slave+' not found')
            continue

        if mc.objectType(ctrl, isType='transform') or mc.objectType(ctrl, isType='joint'):
            master=mc.listRelatives(master,c=1,s=1,pa=1)
            slave=mc.listRelatives(slave,c=1,s=1,pa=1)
        elif mc.objectType(ctrl, isType='nurbsCurve') or mc.objectType(ctrl, isType='nurbsSurface'):
            master=[master]
            slave=[slave]
        else:
            mc.warning('No shape found in '+ctrl)
            continue
        if master is None:
            mc.warning('No shape found in master '+master)
            continue
        elif slave is None:
            mc.warning('No shape found in slave '+slave)
            continue
        while len(master)>len(slave):
            master.pop(-1)

        i=0
        for shape in master:
            altshape=slave[i]
            i+=1
            cvs=mc.getAttr(shape+'.cp', s=1)
            altcvs=mc.getAttr(altshape+'.cp', s=1)
            for cv in range(cvs):
                cp='.cp['+str(cv)+']'
                if space=='ws':
                    pos=mc.xform(shape+cp,q=1,ws=1,t=1)
                    pos[axis]*=-1
                    mc.xform(altshape+cp,ws=1,t=pos)

                #WIP
                elif space=='os':
                    pos=mc.xform(shape+cp,q=1,os=1,t=1)
                    pos[axis]*=-1
                    mc.xform(altshape+cp,os=1,t=pos)

    print('__DONE__')