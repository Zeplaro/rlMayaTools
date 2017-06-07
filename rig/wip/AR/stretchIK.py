import maya.cmds as mc

for letter in 'ABCDE':
    mc.addAttr('platform_ctrl_'+letter, ln='stretch', at='double', min=0, max=1, dv=0, h=0, k=1)
    mc.addAttr('platform_ctrl_'+letter, ln='maxStretch', at='double', min=1, max=4, dv=2, h=0, k=1)
    mc.addAttr('platform_ctrl_'+letter, ln='minStretch', at='double', min=0.25, max=1, dv=1, h=0, k=1)
    for num in range(1, 5):
        if letter == 'E' and num>2:
            continue
        dist = mc.createNode('distanceBetween', n='distB_'+letter+'_'+str(num))
        mc.connectAttr('loc_'+letter+'_btm_'+str(num)+'.worldMatrix', dist+'.inMatrix1')
        mc.connectAttr('loc_'+letter+'_top_'+str(num)+'.worldMatrix', dist+'.inMatrix2')

        mult = mc.createNode('multiplyDivide', n='multD_'+letter+'_'+str(num))
        mc.setAttr(mult+'.operation', 2)
        mc.setAttr(mult+'.input2X', mc.getAttr(dist+'.distance'))
        mc.connectAttr(dist+'.distance', mult+'.input1X')

        clamp = mc.createNode('clamp', n='clamp_'+letter+'_'+str(num))
        mc.connectAttr(mult+'.outputX', clamp+'.inputR')
        mc.connectAttr('platform_ctrl_'+letter+'.maxStretch', clamp+'.maxR')
        mc.connectAttr('platform_ctrl_'+letter+'.minStretch', clamp+'.minR')

        blend = mc.createNode('blendColors', n='blendC_'+letter+'_'+str(num))
        mc.setAttr(blend+'.color2', 1, 1, 1)
        mc.connectAttr('platform_ctrl_'+letter+'.stretch', blend+'.blender')
        mc.connectAttr(clamp+'.outputR', blend+'.color1R')

        mc.connectAttr(blend+'.outputR', 'jnt_'+letter+'_ft_btm_'+str(num)+'.scaleY')
        mc.connectAttr(blend+'.outputR', 'jnt_'+letter+'_ft_mid_'+str(num)+'.scaleY')

        mc.connectAttr(blend+'.outputR', 'jnt_'+letter+'_bk_btm_'+str(num)+'.scaleY')
        mc.connectAttr(blend+'.outputR', 'jnt_'+letter+'_bk_mid_'+str(num)+'.scaleY')

        mc.connectAttr(blend+'.outputR', 'jnt_main_'+letter+'_btm_'+str(num)+'.scaleY')
        mc.connectAttr(blend+'.outputR', 'jnt_main_'+letter+'_mid_'+str(num)+'.scaleY')
