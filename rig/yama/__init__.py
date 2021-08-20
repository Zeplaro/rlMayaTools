import maya.cmds as mc
import nodes.depend as dpn


ntc = dpn.node_to_class
ntcs = dpn.nodes_to_classes


def ls(*args, **kwargs):
    return ntcs(mc.ls(*args, **kwargs))
