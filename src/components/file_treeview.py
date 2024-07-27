import pathlib
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QHeaderView, QMainWindow, QTreeWidgetItem)
from qfluentwidgets.components.widgets import RoundMenu, TreeWidget


class DirectoryTree(TreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(['文件名', '文件路径'])
        self.setBorderVisible(True)
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # self.setColumnHidden(1, True)
        self.itemChanged.connect(self._on_item_changed)
        # self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_menu)

    def load_dir(self, path: pathlib.Path | str):
        self.clear()
        root_path = pathlib.Path(path)
        if not root_path.is_dir():
            raise ValueError(f"{root_path} is not a directory")

        root_item = QTreeWidgetItem(self, [root_path.name, str(root_path)])
        root_item.setFlags(root_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        root_item.setCheckState(0, Qt.CheckState.Unchecked)
        self.addTopLevelItem(root_item)
        self._load_directory(root_path, root_item)
        root_item.setExpanded(True)

    def get_current_selected_files(self) -> list[tuple[str, str]]:
        selected_files: list[tuple[str, str]] = []
        self._get_checked_items(self.invisibleRootItem(), selected_files)
        return selected_files

    def _load_directory(self, path: pathlib.Path, parent: QTreeWidgetItem):
        if not path.exists():
            return

        for entry in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name)):
            if entry.is_dir():
                child = QTreeWidgetItem(parent, [entry.name, str(entry)])
                child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                child.setCheckState(0, Qt.CheckState.Unchecked)
                self._load_directory(entry, child)
            else:
                child = QTreeWidgetItem(parent, [entry.name, str(entry)])
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setCheckState(0, Qt.CheckState.Unchecked)

    def _on_item_changed(self, item: QTreeWidgetItem, column: int):
        if column != 0:
            return
        if item.parent() is None:
            if item.checkState(0) == Qt.CheckState.Checked:
                self._check_child(item)
            elif item.checkState(0) == Qt.CheckState.Unchecked:
                self._uncheck_child(item)
        else:
            if item.checkState(0) == Qt.CheckState.Checked:
                self._check_child(item)
                self._check_parent(item)
            elif item.checkState(0) == Qt.CheckState.Unchecked:
                self._uncheck_child(item)
                self._uncheck_parent(item)
            if not self._is_all_childs_checked(item):
                self._partially_check_parent(item)

    def _check_child(self, parent_item: QTreeWidgetItem):
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            child_item.setCheckState(0, Qt.CheckState.Checked)
            if child_item.childCount() > 0:
                self._check_child(child_item)

    def _uncheck_child(self, parent_item: QTreeWidgetItem):
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            child_item.setCheckState(0, Qt.CheckState.Unchecked)
            if child_item.childCount() > 0:
                self._uncheck_child(child_item)

    def _check_parent(self, child_item: QTreeWidgetItem):
        parent_item = child_item.parent()
        if parent_item is None:
            return
        all_checked = all(
                parent_item.child(i).checkState(0) != Qt.CheckState.Unchecked
                        for i in range(parent_item.childCount())
                )
        if all_checked:
            parent_item.setCheckState(0, Qt.CheckState.Checked)
        else:
            parent_item.setCheckState(0, Qt.CheckState.PartiallyChecked)
        if parent_item.parent() is not None:
            self._check_parent(parent_item)

    def _uncheck_parent(self, child_item: QTreeWidgetItem):
        parent_item = child_item.parent()
        if parent_item is None:
            return
        all_unchecked = all(
                parent_item.child(i).checkState(0) == Qt.CheckState.Unchecked
                        for i in range(parent_item.childCount())
                )
        if all_unchecked:
            parent_item.setCheckState(0, Qt.CheckState.Unchecked)
        else:
            parent_item.setCheckState(0, Qt.CheckState.PartiallyChecked)
        if parent_item.parent() is not None:
            self._uncheck_parent(parent_item)

    def _partially_check_parent(self, child_item: QTreeWidgetItem):
        parent_item = child_item.parent()
        if parent_item is None:
            return
        parent_item.setCheckState(0, Qt.CheckState.PartiallyChecked)
        if parent_item.parent() is not None:
            self._partially_check_parent(parent_item)

    def _is_all_childs_checked(self, parent_item: QTreeWidgetItem):
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.checkState(0) != Qt.CheckState.Checked:
                return False
            if child_item.childCount() > 0 and not self._is_all_childs_checked(child_item):
                return False
        return True

    def _open_menu(self, position):
        menu = RoundMenu()
        delete_action = QAction('删除该节点', self)
        delete_action.triggered.connect(self._delete_node)

        show_current_selected_files = QAction('显示当前选中的文件', self)
        show_current_selected_files.triggered.connect(lambda: print(self.get_current_selected_files()))

        menu.addAction(show_current_selected_files)
        menu.addAction(delete_action)
        menu.exec(self.viewport().mapToGlobal(position))

    def _delete_node(self):
        if selected_indexes := self.selectedIndexes():
            selected_index = selected_indexes[0]
            self.model().removeRow(selected_index.row(), selected_index.parent())

    def _get_checked_items(self, item, selected_files):
        if item.checkState(0) == Qt.CheckState.Checked:
            path = item.text(1)
            relative_path = pathlib.Path(path).relative_to(pathlib.Path(self.topLevelItem(0).text(1)))
            selected_files.append((item.text(0), str(relative_path)))
        for i in range(item.childCount()):
            self._get_checked_items(item.child(i), selected_files)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Directory Tree with Checkboxes")
        self.setGeometry(100, 100, 600, 400)
        self.directory_tree = DirectoryTree()
        self.setCentralWidget(self.directory_tree)
        self.populate_directory_tree()

    def populate_directory_tree(self):
        self.directory_tree.load_dir(pathlib.Path(r"E:\load\python\Project\VideoFusion\src"))

    def get_current_selected_files(self):
        return self.directory_tree.get_current_selected_files()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
