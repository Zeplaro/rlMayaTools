import maya.cmds as mc
import transform
import joint
import mesh
import nurbs
import skinCluster
import shape
import depend
# reload(transform)
# reload(joint)
# reload(mesh)
# reload(nurbs)
# reload(skinCluster)
# reload(shape)
# reload(depend)

supported_class = {'dagNode': 'dag',
                   'transform': 'transform',
                   'nurbsCurve': 'nurbsCurve',
                   'skinCluster': 'skinCluster',
                   'joint': 'joint',
                   'mesh': 'mesh',
                   'shape': 'shape',
                   }


def node_to_class(obj, node_type=None):
    if not node_type:
        node_type = mc.nodeType(obj)
    if node_type == 'transform':
        print('Initializing Transform node')
        return transform.Transform(obj)
    elif node_type == 'joint':
        print('Initializing Joint node')
        return joint.Joint(obj)
    elif node_type == 'mesh':
        print('Initializing Mesh node')
        return mesh.Mesh(obj)
    elif node_type == 'nurbsCurve':
        print('Initializing NurbsCuvre node')
        return nurbs.NurbsCurve(obj)
    elif node_type == 'skinCluster':
        print('Initializing SkinCluster node')
        return skinCluster.SkinCluster(obj)
    elif node_type == 'shape':
        print('Initializing Shape node')
        init_node = shape.Shape(obj)
        return init_node
    elif inherited_type(obj):
        print('found type: {}'.format(inherited_type(obj)))
        return node_to_class(obj, node_type=inherited_type(obj))
    else:
        print('Initializing Depend node')
        return depend.Depend(obj)


def inherited_type(obj):
    node_types = mc.nodeType(obj, inherited=True)[::-1]
    for node_type in node_types:
        if node_type in supported_class:
            return node_type
    return None


def get_sel(flatten=True, long=True):
    return mc.sl(sl=True, flatten=flatten, long=long)
