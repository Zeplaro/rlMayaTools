import maya.cmds as mc
import rig.getAxis as ga

def do_shapeMirror(mirAxis='x', os=False):
    '''
    Mirror objects shape on defined axis in world or object space
    :param str mirAxis: world axis on wich you want to mirror 'x'(default), 'y', 'z'
    __WIP__:param bool os: False(default) mirror on world space, True mirror on object space
    
    TODO: pop cluster shape in shape list
    '''

    #defining index of mirAxis to mirror on choosen axis
    if mirAxis== 'z':
        mirAxis=2
    elif mirAxis== 'y':
        mirAxis=1
    else:
        mirAxis=0

    ctrls=mc.ls(sl=1)
    for ctrl in ctrls:
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
            continue
        if not mc.objExists(slave):
            continue

        #______WIP_____
        #getting ctrls axis in case of object space
        table=ga.getMirrorTable(master,slave)
        print(table)
        table[mirAxis]*=-1
        print(table)

        #Checking if the selection is valid
        if mc.objectType(ctrl, isType='transform') or mc.objectType(ctrl, isType='joint'):
            master=mc.listRelatives(master,c=1,s=1,pa=1, type='nurbsCurve') or []
            slave=mc.listRelatives(slave,c=1,s=1,pa=1, type='nurbsCurve') or []
        elif mc.objectType(ctrl, isType='nurbsCurve'):
            master=[master]
            slave=[slave]
        else:
            continue

        #checking nbr of shapes in master and slave
        while len(master)>len(slave):
            master.pop(-1)

        i=0
        for shape in master:
            cvs=mc.getAttr(shape+'.cp', s=1)
            altcvs=mc.getAttr(slave[i]+'.cp', s=1)
            for cv in range(cvs):
                cp='.cp['+str(cv)+']'
                if not os:
                    pos=mc.xform(shape+cp,q=1,ws=1,t=1)
                    pos[mirAxis]*=-1
                    mc.xform(slave[i]+cp,ws=1,t=pos)

                #________WIP_________
                else:
                    pos=mc.xform(shape+cp,q=1,os=1,t=1)
                    for k in range(3):
                        pos[k]=pos[k]*table[k]
                    mc.xform(slave[i]+cp,os=1,t=pos)
            i+=1
    mc.select(ctrls,r=1)
    print('__DONE__')