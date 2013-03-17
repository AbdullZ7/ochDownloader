import weakref

from PySide.QtGui import *
from PySide.QtCore import *

from qt.tree_view import TreeView


class Tab(QWidget):
    def __init__(self, parent, decrypt_manager):
        # TODO: add import crypted file (+ link),
        # it should create a DownloadItem
        QWidget.__init__(self)

        self.weak_parent = weakref.ref(parent)
        self.decrypt_manager = decrypt_manager
        self.running = False

        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)

        headers = ("hidden_id_item", _("File Name"), _("Status"))
        self.tree_view = TreeView(headers)
        self.tree_view.setColumnHidden(0, True)

        self.vbox.addWidget(self.tree_view)

    @property
    def parent(self):
        return self.weak_parent()

    def setup_tab(self):
        if self.parent.tab.indexOf(self) < 0:
            self.setLayout(self.vbox)
            tab_index = 2
            self.parent.tab.insertTab(tab_index, self, _('Decrypter'))
            self.btn_close = QPushButton()
            self.btn_close.setFixedHeight(12)
            self.btn_close.setFixedWidth(12)
            self.btn_close.clicked.connect(self.on_close)
            self.parent.tab.tabBar().setTabButton(tab_index, QTabBar.RightSide, self.btn_close)

    def on_close(self):
        tab_index = self.parent.tab.indexOf(self)
        if tab_index >= 0:
            self.parent.tab.removeTab(tab_index)
            #self.clear_complete()

    def clear_complete(self):
        for row in self.items[:]:
            if row[2] is not None:
                self.remove_row(row[0])

    def switch_tab(self):
        tab_index = self.parent.tab.indexOf(self)
        if tab_index >= 0:
            self.parent.tab.setCurrentIndex(tab_index)

    def on_import(self):
        pass

    def store(self, download_item):
        item = [download_item.id, download_item.name, None]
        self.tree_view.append_item(item)

        if not self.running:
            self.running = True
            self.timer = self.parent.idle_timeout(1000, self.update_)

    def update_(self):
        # TODO: clear complete items on tab close
        # TODO: Add icons (complete, running, queue)
        # this gets call even if the tab is closed
        items = self.decrypt_manager.get_active_items()
        self.decrypt_manager.update()
        for item in items:
            row = self.tree_view.rows_buffer[item.id_item]
            row[2] = item.status
        self.tree_view.model.refresh()

        if not self.decrypt_manager.active_items:
            self.running = False
            self.timer.stop()