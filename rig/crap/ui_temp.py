#!/usr/bin/env python
# coding:utf-8
""":mod:`renamerUI`
===================================

.. module::
   :platform: Unix
   :synopsis: Renaming tool
   :author: goco
   :date: 2017.06

"""
# --------------------------------------------------------------------------------------------------
# Python built-in modules import
# --------------------------------------------------------------------------------------------------


import webbrowser


# --------------------------------------------------------------------------------------------------
# Third-party modules import
# --------------------------------------------------------------------------------------------------


import maya.cmds as mc
import re
from Qt import QtGui, QtWidgets, QtCore
from mayaBase.contextLib import WaitCursor
from mayaTools.renamer import core, settings


# --------------------------------------------------------------------------------------------------
# Mikros modules import
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------


# QCollapsibleWidget class
class QCollapsibleWidget(QtWidgets.QGroupBox):
    '''Creates a widget similar to the Maya FrameLayout Widget with some additional behaviour.'''

    def __init__(self, parent=None, **kwargs):
        '''Init'''

        QtWidgets.QGroupBox.__init__(self, parent=parent)

        self.setObjectName("collapsible_wdg")

        self.isCollapsed = False
        self.mainLayout = None
        self.titleFrame = None
        self.contentFrame = None
        self.contentLayout = None
        self.frameLayout = None

        self.title_label = kwargs.pop("title", "")

        self.setupUi()

    def addContentWidget(self, widget):
        '''Add widget to the layout

            :param QtWidgets.QWidget widget: Widget to add
        '''

        self.contentLayout.addWidget(widget)

    def initTitleButton(self):
        ''' Init the title button'''

        self.titleFrame = QtWidgets.QToolButton()
        self.titleFrame.setFixedHeight(20)
        self.titleFrame.setAutoRaise(True)
        self.titleFrame.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Fixed)
        self.titleFrame.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.titleFrame.setArrowType(QtCore.Qt.DownArrow)
        self.setTitle(self.title_label)

        self.titleLayout = QtWidgets.QVBoxLayout()
        self.titleLayout.setContentsMargins(0, 0, 0, 0)
        self.titleLayout.setSpacing(0)
        self.titleFrame.setLayout(self.titleLayout)

        self.mainLayout.addWidget(self.titleFrame)

    def initContentFrame(self):
        '''Init the content frame'''

        self.contentFrame = QtWidgets.QFrame()
        self.contentFrame.setContentsMargins(0, 0, 0, 0)

        self.frameLayout = QtWidgets.QHBoxLayout()
        self.frameLayout.setContentsMargins(0, 0, 0, 0)
        self.frameLayout.setSpacing(0)

        self.contentFrame.setLayout(self.frameLayout)

        self.contentLayout = QtWidgets.QVBoxLayout()
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(0)
        self.contentLayout.setAlignment(QtCore.Qt.AlignTop)

        self.frameLayout.addLayout(self.contentLayout)
        self.mainLayout.addWidget(self.contentFrame)

    def toggleCollapsed(self):
        '''Toggle the collapsed state'''

        if self.isCollapsed:
            self.setUnCollapsed()
        else:
            self.setCollapsed()

    def setCollapsed(self):
        '''Set collapsed state to True'''

        self.contentFrame.setVisible(False)
        self.titleFrame.setArrowType(QtCore.Qt.RightArrow)
        self.isCollapsed = True

    def setUnCollapsed(self):
        '''Set collapsed state to False'''

        self.contentFrame.setVisible(True)
        self.titleFrame.setArrowType(QtCore.Qt.DownArrow)
        self.isCollapsed = False

    def setTitleStyleSheet(self, stylesheet):
        '''Set title stylesheet

            :param str stylesheet: New stylesheet
        '''

        self.titleFrame.setStyleSheet(stylesheet)

    def setTitle(self, titleLabel):
        '''Set title

            :param str titleLabel: New title
        '''

        self.titleFrame.setText(titleLabel)
        return QtWidgets.QGroupBox.setTitle(self, "")

    def setupUi(self):
        '''Setup Ui'''

        self.setContentsMargins(0, 0, 0, 0)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)

        self.initTitleButton()
        self.initContentFrame()

        self.titleFrame.clicked.connect(self.toggleCollapsed)


# IconHighlighter class
class IconHighlighter(QtGui.QSyntaxHighlighter):
    Rules = []
    Formats = {}

    def __init__(self, parent=None):
        '''Init'''

        super(IconHighlighter, self).__init__(parent)

        self.initializeFormats()

        IconHighlighter.Rules.append((QtCore.QRegExp('%parent%'), "parent"))
        IconHighlighter.Rules.append((QtCore.QRegExp('%type%'), "type"))
        IconHighlighter.Rules.append((QtCore.QRegExp('[#]+'), "number"))
        IconHighlighter.Rules.append((QtCore.QRegExp('[@]+'), "letter"))

    @staticmethod
    def initializeFormats():
        '''Initialize formats'''

        normalFormat = QtGui.QTextCharFormat()
        IconHighlighter.Formats['normal'] = normalFormat
        normalFormat.setFontPointSize(9)

        baseFormat = QtGui.QTextCharFormat()
        baseFormat.setFontPointSize(9)

        includeFormat = QtGui.QTextCharFormat(baseFormat)
        includeFormat.setForeground(QtGui.QColor(127, 232, 230))
        IconHighlighter.Formats['parent'] = includeFormat

        excludeFormat = QtGui.QTextCharFormat(baseFormat)
        excludeFormat.setForeground(QtGui.QColor(179, 126, 232))
        IconHighlighter.Formats['type'] = excludeFormat

        allFormat = QtGui.QTextCharFormat(baseFormat)
        allFormat.setForeground(QtGui.QColor(232, 141, 126))
        IconHighlighter.Formats['number'] = allFormat

        allFormat = QtGui.QTextCharFormat(baseFormat)
        allFormat.setForeground(QtGui.QColor(232, 175, 126))
        IconHighlighter.Formats['letter'] = allFormat

    def highlightBlock(self, text):
        '''Highlight a text

            :param str text: text to highlight
        '''

        textLength = len(text)
        self.setFormat(0, textLength, IconHighlighter.Formats["normal"])

        for regex, charFormat in IconHighlighter.Rules:
            i = regex.indexIn(text)
            while i >= 0:
                pos = regex.matchedLength()
                self.setFormat(i, pos, IconHighlighter.Formats[charFormat])
                i = regex.indexIn(text, i + pos)

    def rehighlight(self):
        '''Rehighlight'''

        QtCore.QApplication.setOverrideCursor(QtCore.QCursor(QtCore.Qt.WaitCursor))
        QtCore.QSyntaxHighlighter.rehighlight(self)
        QtCore.QApplication.restoreOverrideCursor()


# CompletionTextEdit class
class CompletionTextEdit(QtWidgets.QTextEdit):

    activated = QtCore.Signal(str)
    returnPressed = QtCore.Signal()

    def __init__(self, parent=None):
        '''Init'''

        super(CompletionTextEdit, self).__init__(parent)
        self.setMinimumWidth(400)
        self.completer = None
        self.moveCursor(QtGui.QTextCursor.End)
        self.setMaximumHeight(30)

    def setCompleter(self, completer):
        '''Set completer

            :param Completer completer: New completer
        '''

        if self.completer:
            self.disconnect(self.completer, 0, self, 0)
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer = completer
        self.completer.activated.connect(self.insertCompletion)

    def insertCompletion(self, completion):
        '''Insert completion

            :param str completion: completion to add
        '''

        tc = self.textCursor()
        extra = (len(completion) - len(self.completer.completionPrefix()))
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        '''Returns text under curson

            :rtype: str
        '''

        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, event):
        '''Set focus in event

            :param QEvent event: event
        '''

        if self.completer:
            self.completer.setWidget(self)
        QtWidgets.QTextEdit.focusInEvent(self, event)

    def emitReturnPressed(self):
        '''Emit return pressed event'''

        self.returnPressed.emit()

    def keyPressEvent(self, event):
        '''Show completion on key pressed

            :param QEvent event: event
        '''

        # Return pressed
        if event.key() == QtCore.Qt.Key_Return:
            if self.completer and self.completer.popup().isVisible():
                event.ignore()
                return
            else:
                self.returnPressed.emit()
                return

        # has ctrl-E been pressed??
        isShortcut = (event.modifiers() == QtCore.Qt.ControlModifier and
                      event.key() == QtCore.Qt.Key_E)
        if (not self.completer or not isShortcut):
            QtWidgets.QTextEdit.keyPressEvent(self, event)

        # ctrl or shift key on it's own??
        ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier, QtCore.Qt.ShiftModifier)
        if ctrlOrShift and not event.text():
            # ctrl or shift key on it's own
            return

        completionPrefix = self.textUnderCursor()

        if (completionPrefix != self.completer.completionPrefix()):
            self.completer.setCompletionPrefix(completionPrefix)

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) +
                    self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)

    def currentText(self):
        '''Returns current text

            :rtype: str
        '''

        return self.toPlainText()

    def text(self):
        '''Returns current text

            :rtype: str
        '''

        return self.toPlainText()


# RenamerUI class
class RenamerUI(QtWidgets.QMainWindow):

    # INIT

    def __init__(self, parent=None):
        '''Init'''

        super(RenamerUI, self).__init__(parent)

    # USEFULL FUNCTIONS

    def checkLineContent(self, line, regex=""):
        '''If the QLineEdit doesn't match with the regex, it changes the border color to red.
            It helps the user to understand that the content is forbidden and the search will not
            work.

            :param QtWidgets.QLineEdit line: QLineEdit to check
            :param str regex: Regex to match with the line
        '''

        pattern = re.compile(regex)
        # Changes the border color to red if the line contains forbidden characters
        if pattern.findall(line.text()):
            line.setStyleSheet("border: 1px solid red;")
        else:
            line.setStyleSheet("")

    # RENAME FUNCTIONS

    def createPreviewTableWidget(self):
        '''Returns a new QTableWidget with specific options: a table to preview the renaming.

            :rtype: boolean
        '''

        ui_widget_tblwdg = QtWidgets.QTableWidget(self)

        ui_widget_tblwdg.setMinimumSize(QtCore.QSize(250, 80))
        ui_widget_tblwdg.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        ui_widget_tblwdg.setTabKeyNavigation(False)
        ui_widget_tblwdg.setProperty("showDropIndicator", False)
        ui_widget_tblwdg.setDragDropOverwriteMode(False)
        ui_widget_tblwdg.setAlternatingRowColors(True)
        ui_widget_tblwdg.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        ui_widget_tblwdg.setShowGrid(False)
        ui_widget_tblwdg.setGridStyle(QtCore.Qt.NoPen)
        ui_widget_tblwdg.setWordWrap(False)
        ui_widget_tblwdg.setCornerButtonEnabled(False)
        ui_widget_tblwdg.setColumnCount(2)
        ui_widget_tblwdg.setRowCount(1)
        ui_widget_tblwdg.horizontalHeader().setVisible(False)
        ui_widget_tblwdg.horizontalHeader().setCascadingSectionResizes(True)
        ui_widget_tblwdg.horizontalHeader().setDefaultSectionSize(220)
        ui_widget_tblwdg.horizontalHeader().setHighlightSections(False)
        ui_widget_tblwdg.horizontalHeader().setMinimumSectionSize(220)
        ui_widget_tblwdg.verticalHeader().setVisible(False)
        ui_widget_tblwdg.verticalHeader().setDefaultSectionSize(20)
        ui_widget_tblwdg.verticalHeader().setHighlightSections(False)
        ui_widget_tblwdg.verticalHeader().setMinimumSectionSize(20)
        ui_widget_tblwdg.setItem(0, 0, QtWidgets.QTableWidgetItem("Current"))
        ui_widget_tblwdg.setItem(0, 1, QtWidgets.QTableWidgetItem("Renamed"))
        ui_widget_tblwdg.item(0, 0).setBackground(QtGui.QColor(60, 60, 60))
        ui_widget_tblwdg.item(0, 1).setBackground(QtGui.QColor(60, 60, 60))
        ui_widget_tblwdg.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        ui_widget_tblwdg.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ui_widget_tblwdg.setStyleSheet("QTableWidget::item { padding: 10px }")

        return ui_widget_tblwdg

    def updatePreviewObjects(self, currentObjects, previewObjects, tblwdg):
        '''Shows old and new names, and indicate with colors errors and warnings

            :param list currentObjects: objects selected (old names)
            :param list previewObjects: new names for the selected objects
            :param QTableWidget tblwg: QTableWidget to update with a new content
        '''

        if not currentObjects or not previewObjects:
            return

        # Clear the content of the table
        self.clearPreviewObjects(tblwdg)

        for index, each in enumerate(previewObjects):
            name = each.split('|')[-1]
            oldName = currentObjects[index].split('|')[-1]

            # Insert a new row with the old and the new names
            rowPosition = tblwdg.rowCount()
            tblwdg.insertRow(rowPosition)
            tblwdg.setItem(rowPosition, 0,
                           QtWidgets.QTableWidgetItem(unicode(oldName)))
            tblwdg.item(rowPosition, 0).setToolTip(currentObjects[index])
            tblwdg.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(unicode(name)))

            isUniqueRename = core.checkUnique(name, currentObjects, previewObjects)
            isReadOnly = core.isReference(currentObjects[index])
            isDagNode = core.isDagNode(currentObjects[index])

            # Add a red background color if the new names aren't unique.
            # The user cannot rename the objects.
            if not isUniqueRename or len(mc.ls(currentObjects[index].split('|')[-1])) > 1:
                tblwdg.item(rowPosition, 1).setBackground(QtGui.QColor(100, 0, 0))
                tblwdg.item(rowPosition, 1).setToolTip("Not a unique name")
                self.canRename = False

            # Add an orange background color if the objects aren't dag nodes.
            # The user cannot rename the objects.
            if not isDagNode:
                tblwdg.item(rowPosition, 1).setBackground(QtGui.QColor(215, 125, 0))
                tblwdg.item(rowPosition, 1).setToolTip("Dag node only")
                self.canRename = False

            # Add an orange background color if the objects are references.
            # The user cannot rename the objects.
            if isReadOnly:
                tblwdg.item(rowPosition, 1).setBackground(QtGui.QColor(215, 125, 0))
                tblwdg.item(rowPosition, 1).setToolTip("Is read only")
                self.canRename = False

    def getRename(self, objects):
        '''Get the new names of the objects

            :param list objects: objects to rename
            :rtype: list
        '''

        # If the base mode is selected: replace the name
        if self.ui_advancedCollapse_grpb.isCollapsed:
            renamedObjects = core.replaceName(objects=objects,
                                              replace=self.ui_basename_lned.text())

        # If the advanced mode is selected:
        else:
            searchText = self.ui_search_lned.text()
            replaceText = self.ui_replace_lned.text()
            prefix = self.ui_prefix_lned.text()
            suffix = self.ui_suffix_lned.text()

            # Add numbering with numbers or letters and change the name
            if self.ui_addNumber_grpb.isChecked():
                if self.ui_numeric_rbtn.isChecked():
                    start = self.ui_startNumeric_lened.text()
                    renamedObjects = core.previewRenameAndNumericNumber(objects=objects,
                                                                        search=searchText,
                                                                        replace=replaceText,
                                                                        prefix=prefix,
                                                                        suffix=suffix,
                                                                        start=start)
                else:
                    start = self.ui_startLetters_lned.text()
                    renamedObjects = core.previewRenameAndLetterNumber(objects=objects,
                                                                       search=searchText,
                                                                       replace=replaceText,
                                                                       prefix=prefix,
                                                                       suffix=suffix,
                                                                       start=start)
            # Change the name without numering
            else:
                renamedObjects = core.searchAndReplace(objects=objects,
                                                       search=searchText,
                                                       replace=replaceText,
                                                       prefix=prefix,
                                                       suffix=suffix)
        return renamedObjects

    def previewRename(self):
        '''Updates the preview list with the new names'''

        # Get the selected objects (old names)
        self.currentObjects = core.getSelectedObjects(longName=False, maximum=15)
        # Get the new names for the selected objects
        self.previewObjects = self.getRename(self.currentObjects)

        # Update the preview list in the QTableWidget
        self.updatePreviewObjects(self.currentObjects, self.previewObjects, self.ui_preview_tblwdg)
        self.ui_previewCollapse_grpb.setUnCollapsed()

    def clearPreviewObjects(self, tblwdg):
        '''Clear the QTableWidget

            :param QTabelWidget tblwdg: Table to clear
        '''

        tblwdg.setRowCount(1)
        self.canRename = True

    def changeStack(self, numeric=True):
        '''Toggle the current stack in the QStackedWidget for add number

            :param boolean numeric: Show the numeric stack if True, else show the Letter stack
        '''

        # Show the numeric numbering
        if numeric:
            self.stack.setCurrentIndex(0)

        # Show the letters numbering
        else:
            self.stack.setCurrentIndex(1)

        # Update the preview rename with the new numbering system
        self.previewRename()

    def rename(self):
        '''Rename the objects and clear the preview list'''

        if self.canRename:
            objects = core.getSelectedObjects()
            renamedObjects = self.getRename(objects)
            core.rename(objects, renamedObjects)
            self.clearPreviewObjects(self.ui_preview_tblwdg)

    # INIT THE UI

    def loadShowAllWindow(self):
        '''Show a new window with all the old and new names for the objects.'''

        with WaitCursor():
            ui_helpDialog_wnd = QtWidgets.QDialog(self)
            ui_helpInterface_vlay = QtWidgets.QVBoxLayout(self)
            ui_helpDialog_wnd.setLayout(ui_helpInterface_vlay)
            ui_helpDialog_wnd.setWindowTitle("Preview All Renamed Objects")
            ui_helpDialog_wnd.setWindowFlags(QtCore.Qt.Window)
            ui_helpDialog_wnd.show()

            # Create a tablewidget and add to it the old and the new names
            ui_showAll_tblwdg = self.createPreviewTableWidget()
            showAllCurrentObjects = core.getSelectedObjects(longName=False)
            showAllPreviewObjects = self.getRename(showAllCurrentObjects)
            self.updatePreviewObjects(showAllCurrentObjects, showAllPreviewObjects, ui_showAll_tblwdg)
            ui_helpInterface_vlay.addWidget(ui_showAll_tblwdg)

    def showHelp(self):
        '''Open the doc in a web browser'''

        renamerLink = 'http://wikianim.mikros.int/doku.php?id=public:toolsressources:maya:renamer'
        webbrowser.open_new(renamerLink)

    def loadPreviewUI(self):
        '''Init the UI of the preview part'''

        ui_preview_grpb = QtWidgets.QGroupBox(self)
        ui_preview_vlay = QtWidgets.QVBoxLayout(self)

        # Preview Table Widget
        self.ui_preview_tblwdg = self.createPreviewTableWidget()
        ui_preview_vlay.addWidget(self.ui_preview_tblwdg)

        # Clear and Show All Buttons
        ui_clear_pbtn = QtWidgets.QPushButton("Clear")
        ui_clear_pbtn.clicked.connect(lambda: [self.clearPreviewObjects(self.ui_preview_tblwdg),
                                               setattr(self, "previewObjects", [])])
        ui_showAll_pbtn = QtWidgets.QPushButton("Show All")
        ui_showAll_pbtn.clicked.connect(self.loadShowAllWindow)
        ui_previewButtons_grpb = QtWidgets.QGroupBox(self)
        ui_previewButtons_hlay = QtWidgets.QHBoxLayout(self)
        ui_previewButtons_hlay.addWidget(ui_clear_pbtn)
        ui_previewButtons_hlay.addWidget(ui_showAll_pbtn)
        ui_previewButtons_grpb.setLayout(ui_previewButtons_hlay)
        ui_preview_vlay.addWidget(ui_previewButtons_grpb)

        # To collapse GroupBox
        self.ui_previewCollapse_grpb = QCollapsibleWidget(self, title='Preview')
        self.ui_previewCollapse_grpb.setCollapsed()
        self.ui_previewCollapse_grpb.addContentWidget(ui_preview_grpb)
        ui_preview_grpb.setLayout(ui_preview_vlay)
        self.ui_interface_vblay.addWidget(self.ui_previewCollapse_grpb)

    def loadBasenameUI(self):
        '''Init the UI of basename input'''

        ui_basename_grpb = QtWidgets.QGroupBox(self)
        ui_basename_flay = QtWidgets.QFormLayout(self)

        self.completer = QtWidgets.QCompleter(settings.SEARCH_LIST, self)
        self.ui_basename_lned = CompletionTextEdit(self)
        self.ui_basename_lned.setCompleter(self.completer)
        self.highlighter = IconHighlighter(self.ui_basename_lned.document())
        self.ui_basename_lned.textChanged.connect(lambda: [self.checkLineContent(line=self.ui_basename_lned,
                                                                                 regex="[^a-zA-Z0-9_:#@%]"),
                                                           self.previewRename()])

        ui_basename_flay.addRow(QtWidgets.QLabel("Basename"), self.ui_basename_lned)
        ui_basename_grpb.setLayout(ui_basename_flay)
        self.ui_interface_vblay.addWidget(ui_basename_grpb)

    def loadAdvancedUI(self):
        '''Init the UI of the advanced mode part'''

        # To collapse GroupBox
        self.ui_advancedCollapse_grpb = QCollapsibleWidget(self, title='Advanced')
        self.ui_advancedCollapse_grpb.setCollapsed()

        self.loadSearchUI()
        self.loadNumberingUI()

        self.ui_interface_vblay.addWidget(self.ui_advancedCollapse_grpb)

    def loadNumberingUI(self):
        '''Init the UI of the numbering part'''

        self.ui_addNumber_grpb = QtWidgets.QGroupBox(self)
        self.ui_addNumber_grpb.setCheckable(True)
        self.ui_addNumber_grpb.setChecked(True)
        self.ui_addNumber_grpb.clicked.connect(self.previewRename)
        self.ui_addNumber_grpb.setTitle("Add Numbers")
        self.ui_addNumber_flay = QtWidgets.QFormLayout(self)
        self.stackNumeric = QtWidgets.QWidget(self)
        self.stackLetters = QtWidgets.QWidget(self)
        self.stack = QtWidgets.QStackedWidget(self)
        self.stack.addWidget(self.stackNumeric)
        self.stack.addWidget(self.stackLetters)

        # Buttons
        ui_addNumberButton_grpb = QtWidgets.QGroupBox(self)
        ui_addNumberButton_vlay = QtWidgets.QVBoxLayout(self)
        self.ui_numeric_rbtn = QtWidgets.QRadioButton(self, "Numeric")
        self.ui_numeric_rbtn.setText("Numeric")
        self.ui_numeric_rbtn.setChecked(True)
        self.ui_numeric_rbtn.toggled.connect(lambda: self.changeStack(numeric=self.ui_numeric_rbtn.isChecked()))
        self.ui_letter_rbtn = QtWidgets.QRadioButton(self, "Letter")
        self.ui_letter_rbtn.setText("Letter")
        self.ui_letter_rbtn.toggled.connect(lambda: self.changeStack(numeric=self.ui_numeric_rbtn.isChecked()))
        ui_addNumberButton_vlay.addWidget(self.ui_numeric_rbtn)
        ui_addNumberButton_vlay.addWidget(self.ui_letter_rbtn)
        ui_addNumberButton_grpb.setLayout(ui_addNumberButton_vlay)
        self.ui_addNumber_flay.addRow(ui_addNumberButton_grpb, self.stack)

        # Numeric
        self.ui_startNumeric_lened = QtWidgets.QLineEdit(self)
        self.ui_startNumeric_lened.setText("001")
        self.ui_startNumeric_lened.textChanged.connect(lambda: [self.checkLineContent(line=self.ui_startLetters_lned,
                                                                                      regex="\D"),
                                                                self.previewRename()])
        ui_numericLayout_flay = QtWidgets.QFormLayout(self)
        ui_numericLayout_flay.addRow("Start", self.ui_startNumeric_lened)
        self.stackNumeric.setLayout(ui_numericLayout_flay)

        # Letters
        self.ui_startLetters_lned = QtWidgets.QLineEdit(self)
        self.ui_startLetters_lned.setText("AAA")
        self.ui_startLetters_lned.textChanged.connect(lambda: [self.checkLineContent(line=self.ui_startLetters_lned,
                                                                                     regex="[^a-zA-Z]"),
                                                               self.previewRename()])
        ui_lettersLayout_flay = QtWidgets.QFormLayout(self)
        ui_lettersLayout_flay.addRow("Start", self.ui_startLetters_lned)
        self.stackLetters.setLayout(ui_lettersLayout_flay)

        self.ui_addNumber_grpb.setLayout(self.ui_addNumber_flay)
        self.ui_advancedCollapse_grpb.addContentWidget(self.ui_addNumber_grpb)

    def loadSearchUI(self):
        '''Init the UI of search and replace part'''

        ui_search_grpb = QtWidgets.QGroupBox(self)
        ui_search_glay = QtWidgets.QGridLayout(self)

        # Replace part
        self.ui_search_lned = QtWidgets.QLineEdit(self)
        self.ui_search_lned.textChanged.connect(lambda: [self.checkLineContent(line=self.ui_search_lned,
                                                                               regex="[^a-zA-Z0-9_:]"),
                                                         self.previewRename()])
        ui_search_pbtn = QtWidgets.QPushButton("x")
        ui_search_pbtn.clicked.connect(self.ui_search_lned.clear)
        ui_search_glay.addWidget(ui_search_pbtn, 0, 2)
        ui_search_glay.addWidget(QtWidgets.QLabel("Search"), 0, 0)
        ui_search_glay.addWidget(self.ui_search_lned, 0, 1)
        self.ui_replace_lned = QtWidgets.QLineEdit(self)
        self.ui_replace_lned.textChanged.connect(lambda: [self.checkLineContent(line=self.ui_replace_lned,
                                                                                regex="[^a-zA-Z0-9_:]"),
                                                          self.previewRename()])
        ui_replace_pbtn = QtWidgets.QPushButton("x")
        ui_replace_pbtn.clicked.connect(self.ui_replace_lned.clear)
        ui_search_glay.addWidget(ui_replace_pbtn, 0, 5)
        ui_search_glay.addWidget(QtWidgets.QLabel("Replace"), 0, 3)
        ui_search_glay.addWidget(self.ui_replace_lned, 0, 4)

        # Prefix part
        self.ui_prefix_lned = QtWidgets.QLineEdit(self)
        self.ui_prefix_lned.textChanged.connect(lambda: [self.checkLineContent(line=self.ui_prefix_lned,
                                                                               regex="[^a-zA-Z0-9_:]"),
                                                         self.previewRename()])
        ui_prefix_pbtn = QtWidgets.QPushButton("x")
        ui_prefix_pbtn.clicked.connect(self.ui_prefix_lned.clear)
        ui_search_glay.addWidget(ui_prefix_pbtn, 1, 2)
        ui_search_glay.addWidget(QtWidgets.QLabel("Prefix"), 1, 0)
        ui_search_glay.addWidget(self.ui_prefix_lned, 1, 1)

        # Suffix part
        self.ui_suffix_lned = QtWidgets.QLineEdit(self)
        self.ui_suffix_lned.textChanged.connect(lambda: [self.checkLineContent(line=self.ui_suffix_lned,
                                                                               regex="[^a-zA-Z0-9_:]"),
                                                         self.previewRename()])
        ui_suffix_pbtn = QtWidgets.QPushButton("x")
        ui_suffix_pbtn.clicked.connect(self.ui_suffix_lned.clear)
        ui_search_glay.addWidget(ui_suffix_pbtn, 1, 5)
        ui_search_glay.addWidget(QtWidgets.QLabel("Suffix"), 1, 3)
        ui_search_glay.addWidget(self.ui_suffix_lned, 1, 4)

        ui_search_grpb.setLayout(ui_search_glay)
        self.ui_advancedCollapse_grpb.addContentWidget(ui_search_grpb)

    def loadUI(self):
        '''Init the UI'''

        self.ui_interface_vblay = QtWidgets.QVBoxLayout(self)
        self.ui_interface_vblay.setSpacing(10)

        self.loadBasenameUI()
        self.loadAdvancedUI()
        self.loadPreviewUI()

        # Rename button
        ui_rename_pbtn = QtWidgets.QPushButton("Rename")
        ui_rename_pbtn.clicked.connect(lambda: self.rename())
        self.ui_interface_vblay.addWidget(ui_rename_pbtn)
        self.previewObjects = []
        ui_interface_spc = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                 QtWidgets.QSizePolicy.Expanding)
        self.ui_interface_vblay.addItem(ui_interface_spc)

        # Menu with help
        ui_centralWidget_wg = QtWidgets.QWidget(self)
        ui_centralWidget_wg.setLayout(self.ui_interface_vblay)
        ui_menuBar_mb = QtWidgets.QMenuBar(self)
        ui_showHelp_act = QtWidgets.QAction("Help", self)
        ui_showHelp_act.triggered.connect(self.showHelp)
        ui_menuBar_mb.addAction(ui_showHelp_act)
        self.setMenuBar(ui_menuBar_mb)
        self.setCentralWidget(ui_centralWidget_wg)

        self.setLayout(self.ui_interface_vblay)
        self.setWindowTitle("Renamer")
        self.setWindowFlags(QtCore.Qt.Window)
