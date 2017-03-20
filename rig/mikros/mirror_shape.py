import maya.cmds as mc
from marsTools.mirror_table import getMirrorValues


def refCtrlShapes_mirror():
  for node in mc.ls(sl=True):
      names = node.split(':')
      name = names[-1]
      if name.startswith('L_'):
          names[-1] = name.replace('L_', 'R_')
          target = ':'.join(names)
      elif name.startswith('R_'):
          names[-1] = name.replace('R_', 'L_')
          target = ':'.join(names)
      else:
          continue
      if not mc.objExists(target):
          continue
      
      src_shapes = mc.listRelatives(node, s=1, pa=1, type='nurbsCurve') or []
      dst_shapes = mc.listRelatives(target, s=1, pa=1, type='nurbsCurve') or []
      
      table=getMirrorValues(node, target)
      
      if len(src_shapes) == len(dst_shapes):
          for src, dst in zip(src_shapes, dst_shapes):
              print src, dst
              mc.connectAttr(src+'.local', dst+'.create', f=1)
              mc.refresh()
              mc.disconnectAttr(src+'.local', dst+'.create')
              mc.scale(table[0],table[1],table[2], dst+'.cp[*]', r=1)

refCtrlShapes_mirror()
