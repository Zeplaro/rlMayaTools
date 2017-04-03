#Print un message dans la command line
import maya.OpenMaya as om
om.MGlobal.displayInfo("my grey info message")

#Add a message attribute
mc.addAttr(sel, at='message', ln='L_eye')

#To append a python script path
#It can be written in a userSetup.py file in your script folder to be load when maya starts
import sys
sys.path.append(r'/datas/laro/rlMayaTools/rig/')


#Fix the copy/paste problem between pycharm and maya
#To put in userSetup.py
# -----------------------------------------------------------------------
# Fix for the clipboard bug when coming from Wing/PyCharm
# -----------------------------------------------------------------------
class ScriptEditorFilter(QObject):
   def eventFilter(self, obj, event):
       if event == QKeySequence.Paste and event.type() == QEvent.KeyPress:
           if isinstance(obj, QTextEdit):
               if obj.objectName().startswith('cmdScrollFieldExecuter'):
                   # Paste clipboard text this way, more reliable than Maya's check.
                   maya_widget = MQtUtil.fullName(long(shiboken.getCppPointer(obj)[0]))
                   mc.cmdScrollFieldExecuter(maya_widget, e=True, it=qApp.clipboard().text())
                   return True
       return False

if hasattr(qApp, '_clipboard_fix'):
   qApp.removeEventFilter(qApp._clipboard_fix)
   del qApp._clipboard_fix
qApp._clipboard_fix = ScriptEditorFilter()
qApp.installEventFilter(qApp._clipboard_fix)