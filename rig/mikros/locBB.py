# LOCATOR center
import maya.cmds as mc


def locator_center():
    components = mc.ls(sl=True, fl=True)
    longueur = len(components)

    totx = 0
    toty = 0
    totz = 0

    for vtx in components:
        position = mc.xform(vtx, q=True, t=True, ws=True)
        print position
        totx = totx + position[0]
        toty = toty + position[1]
        totz = totz + position[2]

        placementX = totx / longueur
        placementY = toty / longueur
        placementZ = totz / longueur

    loc = mc.spaceLocator(n='centered_locator')
    mc.move(placementX, placementY, placementZ, loc)


locator_center()

# BOTTOM BB
import maya.cmds as mc

gnrSel = mc.ls(sl=True)
prems = gnrSel[0]
deuz = gnrSel[1]
keeper = list()
keeper.append(prems)
keeper.append(deuz)
bbox = mc.exactWorldBoundingBox(keeper[0])

bottom = [(bbox[0] + bbox[3]) / 2, bbox[1], (bbox[2] + bbox[5]) / 2]
mc.spaceLocator(a=True, n='locatoreuh')
mc.setAttr('locatoreuh.translate', bottom[0], bottom[1], bottom[2], type='double3')
deucontrainte = mc.parentConstraint('locatoreuh', keeper[1], n='deucontrainte')
mc.delete('deucontrainte')
mc.delete('locatoreuh')

# CENTER BB
import maya.cmds as mc

gnrSel = mc.ls(sl=True)
prems = gnrSel[0]
deuz = gnrSel[1]
keeper = list()
keeper.append(prems)
keeper.append(deuz)
bbox = mc.exactWorldBoundingBox(keeper[0])

center = [(bbox[0] + bbox[3]) / 2, (bbox[1] + bbox[4]) / 2, (bbox[2] + bbox[5]) / 2]
mc.spaceLocator(a=True, n='locatoreuh')
mc.setAttr('locatoreuh.translate', center[0], center[1], center[2], type='double3')
deucontrainte = mc.parentConstraint('locatoreuh', keeper[1], n='deucontrainte')
mc.delete('deucontrainte')
mc.delete('locatoreuh')