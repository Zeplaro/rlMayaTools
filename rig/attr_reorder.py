import maya.cmds as mc
from functools import partial


def launch_ui():

    if mc.window('attrReoderUI', exists=True):
        mc.deleteUI('attrReoderUI')
    AttrReorder()


class AttrReorder():

    obj = None
    attrs = []

    def __init__(self):
        self.main_ui()
        mc.showWindow('attrReoderUI')

    def main_ui(self):

        mc.window('attrReoderUI', title='Attribute reorderer', s=True, rtf=True)
        mc.columnLayout()
        mc.button('reload', l='Reload selected', w=100, command=self.reload_sel)
        mc.rowLayout('rowMain', nc=2)
        mc.columnLayout('columnUpDown')
        mc.button('up', l='^', w=25, command=partial(self.move, 'up'))
        mc.button('down', l='v', w=25, command=partial(self.move, 'down'))
        mc.setParent('..')
        mc.columnLayout('columnAttrs')
        self.radioButton_ui()

    def radioButton_ui(self, sel=None):
        mc.columnLayout('radioButtons', p='columnAttrs')
        mc.radioCollection('attrs')

        self.obj = self.get_obj()
        if not self.obj:
            mc.warning('Select an object')
            return
        self.attrs = self.get_attrs()
        if not self.attrs:
            mc.warning('No reorderable attributes on selection')
            return

        for attr in self.attrs:
            if sel == attr:
                mc.radioButton(attr, sl=True)
            else:
                mc.radioButton(attr)

    @staticmethod
    def get_obj():
        sel = mc.ls(sl=True, fl=True)
        if not sel:
            return None
        else:
            sel = sel[0]
        return sel

    def get_attrs(self):
        attributes = mc.listAttr(self.obj, ud=True, visible=True)
        return attributes

    def reload_sel(self, sel=None, *args):
        mc.deleteUI('radioButtons')
        self.radioButton_ui(sel=sel)

    def move(self, way, *args):
        attr = mc.radioCollection('attrs', q=True, select=True)
        index = self.attrs.index(attr)
        if way == 'up':
            if index > 0:
                new_index = index-1
            else:
                return
        else:
            new_index = index+1
        self.attrs.pop(index)
        self.attrs.insert(new_index, attr)

        for attribute in self.attrs:
            if mc.getAttr('{}.{}'.format(self.obj, attribute), lock=True):
                lock = True
                mc.setAttr('{}.{}'.format(self.obj, attribute), lock=False)
            else:
                lock = False
            mc.deleteAttr('{}.{}'.format(self.obj, attribute))
            mc.undo()
            if lock:
                mc.setAttr('{}.{}'.format(self.obj, attribute), lock=True)

        self.reload_sel(attr)
        return
