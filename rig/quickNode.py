import maya.cmds as mc
from functools import partial

"""

Info:   -curveInfo: si une curve est selectinnee alors le node cree est directement connecte a cette curve.
        -distanceBetween: si deux objets sont selectionnes alors le node est directement connecte entre ces deux objets.

Vous pouvez ajouter ou retirer les nodes de vos choix en les ajoutant a la liste si dessous ligne 61 (attention a donner
le nom exact entre guillemets)

"""


def nodecreation(node, texte, *arg):
    nom = mc.textField(texte, query=True, tx=True)
    sel = mc.ls(sl=True)
    if node == 'curveInfo' and sel:
        newnode = mc.arclen(ch=True)
    elif node == 'distanceBetween' and len(sel) == 2:
        newnode = mc.shadingNode('distanceBetween', au=True, n='distance')
        mc.connectAttr(sel[0] + '.worldMatrix', newnode + '.inMatrix1')
        mc.connectAttr(sel[1] + '.worldMatrix', newnode + '.inMatrix2')
        mc.connectAttr(sel[0] + '.rotatePivotTranslate', newnode + '.point1')
        mc.connectAttr(sel[1] + '.rotatePivotTranslate', newnode + '.point2')
    else:
        if nom != '':
            newnode = mc.shadingNode(node, asUtility=True, n=nom)
        else:
            newnode = mc.shadingNode(node, asUtility=True)
        if node == 'condition':
            mc.setAttr(newnode + '.secondTerm', 1)
            for color in 'RGB':
                mc.setAttr(newnode + '.colorIfTrue'+color, 1)
                mc.setAttr(newnode + '.colorIfFalse'+color, 0)
    print(newnode + ' node created')
    return newnode


def do_quickNode():

    winID = 'mainUI'
    if mc.window(winID, exists=True):
        mc.deleteUI(winID)
    mc.window(winID, t='Quick Node', h=100, w=240, s=True, rtf=True)
    mc.columnLayout(w=200)
    mc.rowLayout(nc=3)
    mc.text('Name :')
    texte=mc.textField(w=203)
    mc.setParent('..')
    mc.rowColumnLayout(nc=6)

    nodes = ['multiplyDivide', 'plusMinusAverage', 'reverse', 'condition', 'setRange', 'distanceBetween',
             'curveInfo', 'addDoubleLinear', 'clamp', 'blendColors', 'remapValue', 'angleBetween']
    for node in nodes:
        try:
            mc.symbolButton(i='//'+mc.resourceManager(nf=node+'.svg')[0], h=40, w=40, ann=node, command=partial(nodecreation, node, texte))
        except:
            buttonName = node
            while len(buttonName) > 6:
                buttonName = buttonName[0:len(buttonName)-1]
            mc.button(l=buttonName, h=40, w=40, ann=node, command=partial(nodecreation, node))

    mc.showWindow()
