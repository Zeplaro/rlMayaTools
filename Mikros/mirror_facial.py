#Mirror Facial shapes_orig and Guides L->R
import maya.cmds as mc

side=['L_','R_']

sel=mc.ls(sl=1)
ctrls=mc.listRelatives('facialDrivers',ad=1)
ctrls = ctrls[::-1]
ctrls=[l for l in ctrls if l.find(side[0])!=-1 and l.find('_orig')!=-1 and l.find('TRASH')==-1 and l.find('Shape')==-1]

for ctrl in ctrls:
    mc.spaceLocator(n=ctrl + '_loc')
    mc.parent(ctrl + '_loc', ctrl,r=1)
    mc.group(em=1, n=ctrl + '_grp')
    mc.parent(ctrl + '_loc', ctrl + '_grp')
    mc.setAttr(ctrl + '_grp.scaleX', -1)
    papa=mc.listRelatives(ctrl.replace(side[0], side[1],1), ap=1)
    mc.parent(ctrl + '_loc', papa)
    for axe in 'xyz':
        mc.setAttr(ctrl + '_loc.s'+axe,1)
    mc.parent(ctrl.replace(side[0], side[1],1), ctrl + '_loc')
    for axe in 'xyz':
        for attr in 'tr':
            mc.setAttr(ctrl.replace(side[0], side[1],1)+'.'+attr+axe,0)
    mc.parent(ctrl.replace(side[0], side[1],1), papa)
    if ctrl=='L_eyeCorner_in_ctrl_orig' or ctrl=='L_eyeCorner_out_ctrl_orig':
        mc.rotate(0,0,180,ctrl.replace(side[0], side[1],1),r=1,os=1)
    mc.delete(ctrl + '_loc', ctrl + '_grp')
guides=[side[0]+'teeth_dn_jnt_GUIDE',side[0]+'teeth_up_jnt_GUIDE']
for guide in guides:
    for axe in 'xyz':
        for attr in 'tr':
            mc.setAttr(guide.replace(side[0],side[1],1)+'.'+attr+axe,mc.getAttr(guide+'.'+attr+axe))
    mc.setAttr(guide.replace(side[0],side[1],1)+'.tx',mc.getAttr(guide+'.tx')*-1)
mc.select(sel,r=1)
