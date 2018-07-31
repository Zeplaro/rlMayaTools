import maya.cmds as mc
from functools import partial

"""
Info:   -curveInfo: si une curve est selectinnee alors le node cree est directement connecte a cette curve.
        -distanceBetween: si deux objets sont selectionnes alors le node est directement connecte entre ces deux objets.

Vous pouvez ajouter ou retirer les nodes de vos choix en les ajoutant a la liste si dessous ligne 52 (attention a donner
le nom exact entre guillemets)
"""


def nodecreation(node, texte, *arg):
    nom = mc.textField(texte, query=True, tx=True)
    sel = mc.ls(sl=True, type='transform')
    if node == 'curveInfo' and sel:
        newnode = mc.arclen(ch=True)
    elif node == 'distanceBetween' and len(sel) == 2:
        newnode = mc.shadingNode('distanceBetween', au=True, n='distance')
        mc.connectAttr('{}.worldMatrix'.format(sel[0]), '{}.inMatrix1'.format(newnode))
        mc.connectAttr('{}.worldMatrix'.format(sel[1]), '{}.inMatrix2'.format(newnode))
        mc.connectAttr('{}.rotatePivotTranslate'.format(sel[0]), '{}.point1'.format(newnode))
        mc.connectAttr('{}.rotatePivotTranslate'.format(sel[1]), '{}.point2'.format(newnode))
    else:
        if nom != '':
            newnode = mc.shadingNode(node, asUtility=True, n=nom)
        else:
            newnode = mc.shadingNode(node, asUtility=True)
        if node == 'condition':
            mc.setAttr('{}.secondTerm'.format(newnode), 1)
            for color in 'RGB':
                mc.setAttr('{}.colorIfTrue{}'.format(newnode, color), 1)
                mc.setAttr('{}.colorIfFalse{}'.format(newnode, color), 0)
    print('{} node created'.format(newnode))
    return newnode


def launch_ui():

    win_id = 'mainUI'
    if mc.window(win_id, exists=True):
        mc.deleteUI(win_id)
    mc.window(win_id, t='Quick Node', h=100, w=240, s=True, rtf=True)
    mc.columnLayout(w=200)
    mc.rowLayout(nc=3)
    mc.text('Name :')
    texte = mc.textField(w=203)
    mc.setParent('..')
    mc.rowColumnLayout(nc=6)

    nodes = ['multiplyDivide', 'plusMinusAverage', 'reverse', 'condition', 'setRange', 'distanceBetween',
             'curveInfo', 'addDoubleLinear', 'clamp', 'blendColors', 'remapValue', 'angleBetween']
    for node in nodes:
        try:
            mc.symbolButton(i='//'.format(mc.resourceManager(nf='{}.svg'.format(node))[0]), h=40, w=40, ann=node, command=partial(nodecreation, node, texte))
        except:
            button_name = node
            while len(button_name) > 6:
                button_name = button_name[0:len(button_name)-1]
            mc.button(l=button_name, h=40, w=40, ann=node, command=partial(nodecreation, node))

    mc.showWindow()
