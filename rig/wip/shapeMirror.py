import maya.cmds as mc
import rig.getAxis as ga

def do_shapeMirror(mirAxis='x', space='ws'):
    '''
    Mirror objects shape on defined axis in world or object space
    :param str mirAxis: world axis on wich you want to mirror 'x'(default), 'y', 'z'
    :param str space: 'ws'(default) mirror on world space, 'os' mirror on object space
    '''

    #defining index of mirAxis to mirror on choosen axis
    if mirAxis== 'z':
        mirAxis=2
    elif mirAxis== 'y':
        mirAxis=1
    else:
        mirAxis=0

    #check what space was choosen
    if space=='os':
        space='os'
    else:
        space='ws'

    for ctrl in mc.ls(sl=1):
        #checking for namespaces
        nspace=ctrl.split(':')
        name=nspace[-1]
        if len(nspace)>1:
            nspace.pop(-1)
            nspace=':'.join(nspace)
            nspace+=':'
        else:
            nspace=''

        #checking for side mark
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

        #getting ctrls axis in case of object space
        masterSpace = ga.do_getAxis(master, space='os')
        slaveSpace = ga.do_getAxis(slave, space='os')
        table=[1,1,1]
        for i in range(3):
            if not masterSpace[i] == slaveSpace[i]:
                table[i]=-1
        table[mirAxis]*=-1 #inverting axis on wich mirAxis is defined
        print(table)


        #Checking if the selection is valid
        if mc.objectType(ctrl, isType='transform') or mc.objectType(ctrl, isType='joint'):
            master=mc.listRelatives(master,c=1,s=1,pa=1)
            slave=mc.listRelatives(slave,c=1,s=1,pa=1)
        elif mc.objectType(ctrl, isType='nurbsCurve') or mc.objectType(ctrl, isType='nurbsSurface'):
            master=[master]
            slave=[slave]
        else:
            mc.warning('No shape found in '+ctrl)
            continue
        #check if a shape as been found in selection
        if master is None:
            mc.warning('No shape found in master '+ctrl)
            continue
        elif slave is None:
            mc.warning('No shape found in slave '+ctrl)
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
                    pos[mirAxis]*=-1
                    mc.xform(altshape+cp,ws=1,t=pos)

                #WIP
                elif space=='os':
                    pos=mc.xform(shape+cp,q=1,os=1,t=1)
                    for i in range(3):
                        pos[i]=pos[i]*table[i]
                    mc.xform(altshape+cp,os=1,t=pos)

    print('__DONE__')