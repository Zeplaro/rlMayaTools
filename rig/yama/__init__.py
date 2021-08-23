import sys

yama_path = '/'.join(__file__.replace('\\', '/').split('/')[:-2])
if yama_path not in sys.path:
    sys.path.append(yama_path)

import maya.cmds as mc
import nodes


yam = nodes.yam
yams = nodes.yams


def ls(*args, **kwargs):
    return yams(mc.ls(*args, **kwargs))


def selected():
    return yams(mc.ls(sl=True, fl=True))
