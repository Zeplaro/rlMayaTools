#Print un message dans la command line
import maya.OpenMaya as om
om.MGlobal.displayInfo("my grey info message")

#To append a python script path
#It can be written in a userSetup.py file in your script folder to be load when maya starts
import sys
sys.path.append(r'D:\....\Work\Python\rlMayaTools')