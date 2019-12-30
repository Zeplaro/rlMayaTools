from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import os
from functools import partial
import shutil


def launch_ui():
    app = QtWidgets.QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    sys.exit(app.exec_())


class MainUI(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.selected = []
        self.root_path = ''
        self.extension_btns = []
        self.ignore_btns = []
        self.file_extensions = set()

        self.ui_layout()
        self.ui_connections()

    def ui_layout(self):
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        self.setGeometry(0, 0, 1500, 800)
        self.setWindowTitle('Duplicate Sorter')

        browse_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(browse_layout)
        self.browse_line = QtWidgets.QLineEdit('D:/Robin/Pictures/Photo/a trier/2019')
        browse_layout.addWidget(self.browse_line)
        self.browse_button = QtWidgets.QPushButton('Browse')
        browse_layout.addWidget(self.browse_button)

        tree_view_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(tree_view_layout)
        self.folder_tree = QtWidgets.QTreeView()
        tree_view_layout.addWidget(self.folder_tree)
        folder_model = QtWidgets.QFileSystemModel()
        folder_model.setReadOnly(True)
        folder_model.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
        folder_model.setRootPath(self.browse_line.text())
        self.folder_tree.setModel(folder_model)
        self.folder_tree.setRootIndex(folder_model.index(self.browse_line.text()))
        self.folder_tree.setAlternatingRowColors(True)
        self.folder_tree.setAnimated(False)
        self.folder_tree.setIndentation(20)
        self.folder_tree.setSortingEnabled(True)
        self.folder_tree.setColumnHidden(1, True)
        self.folder_tree.setColumnHidden(2, True)
        self.folder_tree.setColumnHidden(3, True)
        self.folder_tree.setFixedWidth(300)
        self.folder_tree.setColumnWidth(0, 200)

        self.view = QtWidgets.QTreeWidget()
        tree_view_layout.addWidget(self.view)
        self.view.setAlternatingRowColors(True)
        self.view.setSortingEnabled(True)
        self.view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.view.setColumnCount(3)
        self.view.setHeaderLabels(('Name', 'Type', 'Size'))
        self.view.setColumnWidth(0, 400)
        self.view.setIndentation(0)

        tools_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(tools_layout)

        extension_box = QtWidgets.QGroupBox('Extension')
        tools_layout.addWidget(extension_box)
        self.extension_layout = QtWidgets.QVBoxLayout()
        extension_box.setLayout(self.extension_layout)
        extension_box.setFixedWidth(200)
        extension_btn_layout = QtWidgets.QHBoxLayout()
        self.extension_layout.addLayout(extension_btn_layout)
        self.all_extensions_button = QtWidgets.QPushButton('All')
        extension_btn_layout.addWidget(self.all_extensions_button)
        self.no_extensions_button = QtWidgets.QPushButton('None')
        extension_btn_layout.addWidget(self.no_extensions_button)

        ignore_box = QtWidgets.QGroupBox('Ignore')
        tools_layout.addWidget(ignore_box)
        self.ignore_layout = QtWidgets.QVBoxLayout()
        ignore_box.setLayout(self.ignore_layout)
        ignore_box.setFixedWidth(200)
        ignore_btn_layout = QtWidgets.QHBoxLayout()
        self.ignore_layout.addLayout(ignore_btn_layout)
        self.all_ignore_button = QtWidgets.QPushButton('All')
        ignore_btn_layout.addWidget(self.all_ignore_button)
        self.no_ignore_button = QtWidgets.QPushButton('None')
        ignore_btn_layout.addWidget(self.no_ignore_button)

        action_box = QtWidgets.QGroupBox('Action')
        tools_layout.addWidget(action_box)
        action_layout = QtWidgets.QVBoxLayout()
        action_box.setLayout(action_layout)
        action_box.setFixedWidth(200)
        self.action_button_group = QtWidgets.QButtonGroup()
        for action in ('Delete', 'Copy', 'Move'):
            action_button = QtWidgets.QRadioButton(action)
            self.action_button_group.addButton(action_button)
            action_layout.addWidget(action_button)
            action_button.setChecked(True)
        self.move_line = QtWidgets.QLineEdit('subfolder')
        action_layout.addWidget(self.move_line)
        self.move_line.setFixedWidth(150)

        stats_layout = QtWidgets.QVBoxLayout()
        tools_layout.addLayout(stats_layout)
        self.total_label = QtWidgets.QLabel('Total files : 0')
        stats_layout.addWidget(self.total_label)
        self.selected_label = QtWidgets.QLabel('Selected files : 0')
        stats_layout.addWidget(self.selected_label)
        self.type_label = QtWidgets.QLabel('File types :')
        stats_layout.addWidget(self.type_label)

        process_layout = QtWidgets.QVBoxLayout()
        process_layout.setAlignment(QtCore.Qt.AlignRight)
        tools_layout.addLayout(process_layout)
        self.process_button = QtWidgets.QPushButton('Process')
        self.process_button.setFixedHeight(50)
        self.process_button.setFixedWidth(100)
        process_layout.addWidget(self.process_button)

        self.progress = QtWidgets.QProgressBar()
        main_layout.addWidget(self.progress)

    def ui_connections(self):
        self.folder_tree.clicked.connect(self.populate_view)
        self.browse_button.clicked.connect(self.browse)
        self.browse_line.editingFinished.connect(self.set_root_dir)
        self.view.doubleClicked.connect(self.open_path)
        self.no_extensions_button.clicked.connect(partial(self.check_extensions, 0))
        self.all_extensions_button.clicked.connect(partial(self.check_extensions, 2))
        self.no_ignore_button.clicked.connect(partial(self.check_ignore, 0))
        self.all_ignore_button.clicked.connect(partial(self.check_ignore, 2))
        self.process_button.clicked.connect(self.process)

    def populate_view(self, index):
        self.view.clear()
        self.data = {}
        self.root_path = ''
        if index:
            path = self.folder_tree.model().filePath(index)
            self.file_extensions = set()
            for root, dirs, files in os.walk(path):
                self.total_label.setText('Total files : {}'.format(len(files)))
                root = root.replace('\\', '/')
                self.root_path = root
                for file in files:
                    file_splitted = file.lower().split('.')
                    full_path = os.path.join(root, file)
                    size = round(os.path.getsize(full_path)/1000000, 2)
                    item = QtWidgets.QTreeWidgetItem()
                    self.data[file.lower()] = {'name': file_splitted[0],
                                               'ext': file_splitted[-1],
                                               'item': item,
                                               'full_path': full_path,
                                               'size': size,
                                               }
                    self.file_extensions.add(file_splitted[-1])
                    item.setText(0, file)
                    item.setText(1, file_splitted[-1])
                    item.setText(2, str(size))
                    self.view.addTopLevelItem(item)
                break
            self.type_label.setText('File types : {}'.format(self.file_extensions))
        self.populate_extensions()
        self.highlight()

    def populate_extensions(self):
        for item in self.extension_btns:
            self.extension_layout.removeWidget(item)
            item.hide()
            del item
        for item in self.ignore_btns:
            self.ignore_layout.removeWidget(item)
            item.hide()
            del item
        self.extension_btns = []
        self.ignore_btns = []
        for extension in self.file_extensions:
            ext_btn = QtWidgets.QCheckBox(extension)
            self.extension_btns.append(ext_btn)
            self.extension_layout.insertWidget(self.ignore_layout.count()-1, ext_btn)
            ext_btn.stateChanged.connect(self.highlight)

            ignore_btn = QtWidgets.QCheckBox(extension)
            self.ignore_btns.append(ignore_btn)
            self.ignore_layout.insertWidget(self.ignore_layout.count()-1, ignore_btn)
            ignore_btn.stateChanged.connect(self.highlight)
            ignore_btn.stateChanged.connect(partial(self.lock_extension, ext_btn))

    def check_extensions(self, state):
        for ext in self.extension_btns:
            ext.setCheckState(state)

    def check_ignore(self, state):
        for i in self.ignore_btns:
            i.setCheckState(state)

    @staticmethod
    def lock_extension(ext_btn, state):
        if not state:
            ext_btn.setEnabled(True)
        else:
            ext_btn.setChecked(False)
            ext_btn.setEnabled(False)

    def browse(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(directory=self.browse_line.text())
        self.browse_line.setText(path)
        self.set_root_dir()

    def set_root_dir(self):
        self.browse_line.setText(self.browse_line.text().replace('\\', '/'))
        path = self.browse_line.text()
        if os.path.exists:
            model = self.folder_tree.model()
            model.setRootPath(path)
            self.folder_tree.setRootIndex(model.index(path))

    def highlight(self):
        self.selected = {}
        for file in self.data:
            self.data[file]['item'].setBackground(0, QtGui.QColor(1, 1, 1, 1))
            self.data[file]['item'].setBackground(1, QtGui.QColor(1, 1, 1, 1))
            self.data[file]['item'].setBackground(2, QtGui.QColor(1, 1, 1, 1))
        ignored_extensions = [x.text() for x in self.ignore_btns if x.isChecked()]
        checked_extensions = [x.text() for x in self.extension_btns if x.isChecked()]
        new_data = {}
        for file in self.data:
            if not self.data[file]['ext'] in ignored_extensions:
                new_data[file] = self.data[file]
        file_names = [new_data[file]['name'] for file in new_data]
        count = 0
        for file in new_data:
            if file_names.count(new_data[file]['name']) > 1:
                if new_data[file]['ext'] in checked_extensions:
                    new_data[file]['item'].setBackground(0, QtGui.QColor(255, 0, 0, 50))
                    new_data[file]['item'].setBackground(1, QtGui.QColor(255, 0, 0, 50))
                    new_data[file]['item'].setBackground(2, QtGui.QColor(255, 0, 0, 50))
                    self.selected[file] = new_data[file]
                    count += 1
        self.selected_label.setText('Selected files : {}'.format(count))

    def open_path(self):
        print('Opening in windows exporer')
        os.startfile(self.root_path)

    def process(self):
        print('Processing')
        indexes = self.folder_tree.selectedIndexes()
        if indexes:
            action = self.action_button_group.checkedButton().text()
            if action == 'Move':
                self.move_files()
            elif action == 'Delete':
                self.delete_files()
            else:
                self.copy_files()
            self.populate_view(indexes[0])

    def move_files(self):
        print('Moving files')
        subfolder = self.move_line.text()
        new_root = os.path.join(self.root_path, subfolder)
        if not os.path.exists(new_root):
            os.makedirs(new_root)
        self.progress.setMaximum(len(self.selected))
        self.progress.setValue(0)
        count = 0
        for file in self.selected:
            self.progress.setValue(count)
            new_path = os.path.join(new_root, file)
            shutil.move(self.selected[file]['full_path'], new_path)
            count += 1

    def delete_files(self):
        print('Deleting files')

    def copy_files(self):
        print('Copying files')


def test():
    print('TEST')


if __name__ == '__main__':
    launch_ui()
