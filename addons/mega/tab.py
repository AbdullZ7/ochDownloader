import weakref
import os

from core.api import api

from PySide.QtGui import *
from PySide.QtCore import *

from qt.tree_view import TreeView
from qt import media


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

        self.hbox = QHBoxLayout()
        self.hbox.setContentsMargins(0, 0, 0, 0)

        self.btn_add = QPushButton()
        self.btn_add.setIcon(media.get_icon(media.ADD, media.MEDIUM))
        self.btn_add.setIconSize(QSize(24, 24))
        self.btn_add.clicked.connect(self.on_import)
        self.btn_add.setFixedHeight(35)
        self.btn_add.setMaximumWidth(40)

        self.hbox.addStretch()
        self.hbox.addWidget(self.btn_add)

        self.vbox.addLayout(self.hbox)

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
        dialog = ImportDialog(self.parent)
        if dialog.result() == QDialog.Accepted:
            path = dialog.file_line.text()
            link = dialog.link_line.text()
            if path and link:
                file_path, file_name = os.path.split(path)
                download_item = api.create_download_item(file_name, link)
                download_item.path = file_path
                self.decrypt_manager.add(download_item)
                self.store(download_item)

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


class ImportDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setWindowTitle(_("Mega decrypt importer"))
        self.resize(340, 200)

        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        self.setLayout(vbox)

        hbox = QHBoxLayout()

        self.file_line = QLineEdit()
        self.file_line.setFixedHeight(35)
        self.file_line.setMinimumWidth(1)

        hbox.addWidget(self.file_line)

        btn_examine = QPushButton('...')
        btn_examine.clicked.connect(self.on_examine)
        btn_examine.setFixedHeight(35)
        btn_examine.setMaximumWidth(80)
        hbox.addWidget(btn_examine)

        vbox.addLayout(hbox)

        self.link_line = QLineEdit()
        vbox.addWidget(self.link_line)

        # buttons
        vbox.addStretch()

        hbox_btns = QHBoxLayout()
        vbox.addLayout(hbox_btns)

        hbox_btns.addStretch()

        btn_ok = QPushButton(_('OK'))
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.accept)
        btn_ok.setFixedHeight(35)
        btn_ok.setMaximumWidth(80)
        hbox_btns.addWidget(btn_ok)

        #if hasattr(widget, 'setFocus'):
            #widget.setFocus() #call after creating all of the other widgets.

        self.exec_()
        self.deleteLater()

    def on_examine(self):
        file_name, filter = QFileDialog.getOpenFileName(filter='Crypted Files (*.crypted)')
        if file_name:
            self.file_line.setText(file_name)