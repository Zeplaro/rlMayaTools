import maya.cmds as mc

#target=mc.ls(sl=1,tr=1)
target=['pCube1','pSphere1']

if len(target)==2:
    cmx='cmx_'+target[0]
    mmx='mmx_'+target[0]
    dmx='dmx_'+target[0]
    mc.createNode('multMatrix',n=mmx)
    mc.createNode('decomposeMatrix',n=dmx)
    mc.createNode('composeMatrix',n=cmx)
    mc.connectAttr(target[0]+'.worldMatrix[0]',mmx+'.matrixIn[0]',f=1)
    mc.connectAttr(mmx+'.matrixSum',dmx+'.inputMatrix',f=1)
    
    
print(mc.getAttr(target[1]+'.worldMatrix'))

mc.setAttr(target[1]+'.worldMatrix',[1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.4063983397454831, 0.508604463260997, -0.679709237207857, 1.0])

else:
    print('wrong number of objects')
