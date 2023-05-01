from maya import cmds, mel
from copy import deepcopy


def get_current_shelf():
    """Gets the current shelf name"""
    return mel.eval("tabLayout -q -selectTab $gShelfTopLevel")


def get_shelf_data(shelf=None):
    """
    Gets the given shelf data into a list of dict. To be easily restored using set_shelf_data.
    Instead of using the maya generated shelf file in mel that does not always work between different maya versions.
    :param shelf: str of an existing shelf name
    :return: [dict, dict, ...] list of dict data per shelf item
    """
    button_kwargs = ('imageOverlayLabel', 'command', 'sourceType', 'image', 'annotation', 'doubleClickCommand', 'label')
    menu_kwargs = ('label', 'command', 'sourceType')
    excluded_labels = ('Open', 'Edit', 'Edit Popup', 'Delete')

    if not shelf:
        shelf = get_current_shelf()
    data = []
    for button in cmds.shelfLayout(shelf, query=True, childArray=True) or []:
        ui_type = cmds.objectTypeUI(button)
        if ui_type == 'separator':
            data.append('separator')
        elif ui_type == 'shelfButton':
            button_data = {kwarg: cmds.shelfButton(button, q=True, **{kwarg: True}) for kwarg in button_kwargs}
            button_data['menu'] = []
            for menu in cmds.shelfButton(button, q=True, pma=True) or []:
                for item in cmds.popupMenu(menu, q=True, itemArray=True) or []:
                    if cmds.menuItem(item, q=True, label=True) in excluded_labels:
                        continue
                    menu_data = {kwarg: cmds.menuItem(item, q=True, **{kwarg: True}) or '' for kwarg in menu_kwargs}
                    button_data['menu'].append(menu_data)
            data.append(button_data)
    return data


def set_shelf_data(data, shelf=None):
    """
    Sets the given shelf data from get_shelf_data.
    Instead of using the maya generated shelf file in mel that does not always work between different maya versions.
    :param data: [dict, dict, ...] list of dict data per shelf item
    :param shelf: str of an existing shelf name
    """
    if not shelf:
        shelf = get_current_shelf()
    for button_data in deepcopy(data):  # deepcopy to not alter the given data object or its values with later .pop()
        if button_data == 'separator':
            cmds.separator(width=12, height=35, style='shelf', hr=False, parent=shelf)
        else:
            menu_items = button_data.pop('menu')
            # To replace with cmds.shelfButton(parent=shelf, **button_data) when only using Python 3
            button = cmds.shelfButton(parent=shelf, imageOverlayLabel=button_data['imageOverlayLabel'], sourceType=button_data['sourceType'], image=button_data['image'], label=button_data['label'], command=button_data['command'], annotation=button_data['annotation'], doubleClickCommand=button_data['doubleClickCommand'])
            menu = cmds.shelfButton(button, q=True, pma=True)[0]
            for menu_data in menu_items:
                # To replace with cmds.menuItem(parent=menu, **menu_data) when only using Python 3
                cmds.menuItem(parent=menu, command=menu_data['command'], sourceType=menu_data['sourceType'], label=menu_data['label'])
