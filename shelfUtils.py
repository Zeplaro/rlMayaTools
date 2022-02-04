from maya import cmds, mel


def get_current_shelf():
    return mel.eval("tabLayout -q -selectTab $gShelfTopLevel")


def get_shelf_data(shelf=None):
    button_kwargs = ('imageOverlayLabel', 'command', 'sourceType', 'image', 'annotation', 'doubleClickCommand', 'label')
    menu_kwargs = ('label', 'command', 'sourceType')

    if not shelf:
        shelf = get_current_shelf()
    data = []
    for button in cmds.shelfLayout(shelf, query=True, childArray=True) or []:
        uiType = cmds.objectTypeUI(button)
        button_data = {}
        if uiType == 'separator':
            button_data = 'separator'
        if uiType == 'shelfButton':
            button_data = {kwarg: cmds.shelfButton(button, q=True, **{kwarg: True}) for kwarg in button_kwargs}
            button_data['submenus'] = []
            button_data['submenus_data'] = {}
            for menu in cmds.shelfButton(button, q=True, pma=True) or []:
                for item in cmds.popupMenu(menu, q=True, itemArray=True) or []:
                    button_data['submenus'].append(item)
                    button_data['submenus_data'][item] = {kwarg: cmds.menuItem(item, q=True, **{kwarg: True}) for kwarg in menu_kwargs}
        data.append(button_data)
    return data


def set_shelf_data(data, shelf=None):
    if not shelf:
        shelf = get_current_shelf()
    for button in data:
        if button == 'separator':
            cmds.separator(width=12, height=35, style='shelf', hr=False, parent=shelf)
        else:
            submenus = button.pop('submenus')
            submenus_data = button.pop('submenus_data')
            button = cmds.shelfButton(parent=shelf, **button)
            menu = cmds.shelfButton(button, q=True, pma=True)[0]
            for item in submenus:
                cmds.menuItem(parent=menu, **submenus_data[item])
