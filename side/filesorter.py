from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import os
from functools import partial


def launch_ui():
    app = QtWidgets.QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    sys.exit(app.exec_())


class MainUI(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui_layout()
        self.ui_connections()
        self.data = {}
        self.selected = []

    def ui_layout(self):
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        self.setGeometry(0, 0, 1500, 800)
        self.setWindowTitle('File Sorter')

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
        extension_layout = QtWidgets.QVBoxLayout()
        extension_box.setLayout(extension_layout)
        extension_box.setFixedWidth(200)
        extensions = ('jpeg', 'jpg', 'png', 'raf', 'dng', 'tiff', 'xmp')
        self.extensions = []
        for extension in extensions:
            item = QtWidgets.QCheckBox(extension)
            item.setTristate(False)
            self.extensions.append(item)
            extension_layout.addWidget(item)
        extension_btn_layout = QtWidgets.QHBoxLayout()
        extension_layout.addLayout(extension_btn_layout)
        self.all_extensions_button = QtWidgets.QPushButton('All')
        extension_btn_layout.addWidget(self.all_extensions_button)
        self.no_extensions_button = QtWidgets.QPushButton('None')
        extension_btn_layout.addWidget(self.no_extensions_button)

        ignore_box = QtWidgets.QGroupBox('Ignore')
        tools_layout.addWidget(ignore_box)
        ignore_layout = QtWidgets.QVBoxLayout()
        ignore_box.setLayout(ignore_layout)
        ignore_box.setFixedWidth(200)
        ignores = ('jpeg', 'jpg', 'png', 'raf', 'dng', 'tiff', 'xmp')
        self.ignored = []
        for ignore in ignores:
            item = QtWidgets.QCheckBox(ignore)
            item.setTristate(False)
            self.ignored.append(item)
            ignore_layout.addWidget(item)
        ignore_btn_layout = QtWidgets.QHBoxLayout()
        ignore_layout.addLayout(ignore_btn_layout)
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
        move_line = QtWidgets.QLineEdit('subfolder')
        action_layout.addWidget(move_line)
        move_line.setFixedWidth(150)

        stats_layout = QtWidgets.QVBoxLayout()
        tools_layout.addLayout(stats_layout)
        self.total_label = QtWidgets.QLabel('Total files : 0')
        stats_layout.addWidget(self.total_label)
        self.selected_label = QtWidgets.QLabel('Selected files : 0')
        stats_layout.addWidget(self.selected_label)
        self.type_label = QtWidgets.QLabel('File types :')
        stats_layout.addWidget(self.type_label)

        self.doit_button = QtWidgets.QPushButton('Do it')
        self.doit_button.setFixedHeight(100)
        self.doit_button.setFixedWidth(100)
        tools_layout.addWidget(self.doit_button)

    def ui_connections(self):
        self.folder_tree.clicked.connect(self.populate_view)
        self.browse_button.clicked.connect(self.browse)
        self.browse_line.editingFinished.connect(self.set_root_dir)
        self.view.doubleClicked.connect(self.open_path)
        for ext in self.extensions:
            ext.stateChanged.connect(self.highlight)
        for i, ext in enumerate(self.ignored):
            ext.stateChanged.connect(self.highlight)
            ext.stateChanged.connect(partial(self.lock_extension, i))
        self.no_extensions_button.clicked.connect(partial(self.check_extensions, 0))
        self.all_extensions_button.clicked.connect(partial(self.check_extensions, 2))
        self.no_ignore_button.clicked.connect(partial(self.check_ignore, 0))
        self.all_ignore_button.clicked.connect(partial(self.check_ignore, 2))
        self.doit_button.clicked.connect(self.process)

    def check_extensions(self, state):
        for ext in self.extensions:
            ext.setCheckState(state)

    def check_ignore(self, state):
        for i in self.ignored:
            i.setCheckState(state)

    def lock_extension(self, i, state):
        if not state:
            self.extensions[i].setEnabled(True)
        else:
            self.extensions[i].setChecked(False)
            self.extensions[i].setEnabled(False)

    def populate_view(self, index):
        self.view.clear()
        self.data = {}
        if index:
            path = self.folder_tree.model().filePath(index)
            extensions = set()
            for root, dirs, files in os.walk(path):
                self.total_label.setText('Total files : {}'.format(len(files)))
                root = root.replace('\\', '/')
                for i, file in enumerate(files):
                    file_splitted = file.lower().split('.')
                    full_path = os.path.join(root, file)
                    size = round(os.path.getsize(full_path)/1000000, 2)
                    item = QtWidgets.QTreeWidgetItem()
                    self.data[file.lower()] = {'name': file_splitted[0],
                                               'ext': file_splitted[-1],
                                               'item': item,
                                               'root_path': root,
                                               'full_path': full_path,
                                               'size': size,
                                               }
                    extensions.add(file_splitted[-1])
                    item.setText(0, file)
                    item.setText(1, file_splitted[-1])
                    item.setText(2, str(size))
                    self.view.addTopLevelItem(item)
                break
            self.type_label.setText('File types : {}'.format(extensions))
        self.highlight()

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
        for file in self.data:
            self.data[file]['item'].setBackground(0, QtGui.QColor(1, 1, 1, 1))
            self.data[file]['item'].setBackground(1, QtGui.QColor(1, 1, 1, 1))
            self.data[file]['item'].setBackground(2, QtGui.QColor(1, 1, 1, 1))
        self.selected = []
        ignored_extensions = [x.text() for x in self.ignored if x.isChecked()]
        checked_extensions = [x.text() for x in self.extensions if x.isChecked()]
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
                    self.selected.append(new_data[file]['full_path'])
                    count += 1
        self.selected_label.setText('Selected files : {}'.format(count))

    def open_path(self, index):
        print('Opening in windows exporer')
        file = self.view.model().itemData(index)[0].lower()
        os.startfile(self.data[file.lower()]['root_path'])

    def process(self):
        print('Processing')


def test():
    print('TEST')


if __name__ == '__main__':
    launch_ui()
