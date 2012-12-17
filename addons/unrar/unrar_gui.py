import weakref
import re
import os
import logging
logger = logging.getLogger(__name__)

from core.api import api

from unrar import UnRAR

from PySide.QtGui import *
from PySide.QtCore import *

from qt.list_model import SimpleListModel

COMPLETE, ERR_MSG = range(2)


class UnRARGUI:
    def __init__(self, parent):
        self.weak_parent = weakref.ref(parent)
        self.unrar = UnRAR()
        self.unrar_tab = UnRARTab(self.unrar, parent)
        self.tab_widget = QWidget()
        self.tab_widget.setLayout(self.unrar_tab)

    @property
    def parent(self):
        return self.weak_parent()
    
    def add_file(self, download_item):
        self.file_name = download_item.name
        if self.can_extract():
            file_path = os.path.join(download_item.path, self.file_name)
            self.unrar.add(file_path, download_item.path, download_item.id) #file_path, dest_path
            self.add_tab()
            self.unrar_tab.store_items([download_item, ])
    
    def add_tab(self):
        if self.parent.tab.indexOf(self.tab_widget) < 0:
            index_page = 2
            self.parent.tab.insertTab(index_page, self.tab_widget, _('Extracting'))
            btn_close = QPushButton(self.parent)
            btn_close.setFixedHeight(12)
            btn_close.setFixedWidth(12)
            btn_close.clicked.connect(self.on_close_tab)
            self.parent.tab.tabBar().setTabButton(index_page, QTabBar.RightSide, btn_close)
    
    def on_close_tab(self):
        index_page = self.parent.tab.indexOf(self.tab_widget)
        if index_page >= 0:
            self.unrar_tab.clear_list()
            self.parent.tab.removeTab(index_page)
    
    def can_extract(self):
        pattern = '^(?P<name>.*?)(?P<part>\.part\d+)?(?P<ext>\.rar|\.r\d+)$'
        m = re.match(pattern, self.file_name)
        if m is not None: #is rar file
            if not self.has_segments_left(pattern, m.group('name')):
                if m.group('part') is not None: #new ext. style
                    self.file_name = "".join((m.group('name'), ".part1.rar"))
                else: #single part or old ext. style
                    self.file_name = "".join((m.group('name'), ".rar"))
                return True
        return False
    
    def has_segments_left(self, pattern, name):
        """"""
        for download_item in api.get_active_downloads().values() + api.get_queue_downloads().values() + api.get_stopped_downloads().values():
            m = re.match(pattern, download_item.name)
            if m is not None:
                if name == m.group('name'):
                    return True
        return False


class UnRARTab(QVBoxLayout):
    def __init__(self, unrar, parent):
        #TODO: cargar solo la lista al cambiar de pestania. no destruir todo.
        QVBoxLayout.__init__(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        
        self.unrar = unrar
        self.weak_parent = weakref.ref(parent)
        
        self.tree_view = QTreeView()
        #
        #self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.tree_view.customContextMenuRequested.connect(self.context_menu)
        #
        #listview look
        self.tree_view.setWordWrap(True) #search textElideMode
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setIndentation(0)
        self.tree_view.setAlternatingRowColors(True)
        #
        self.items = []
        self.rows_buffer = {} #{id_item: row_obj, }
        headers = ["hidden_id_item", _("File Name"), _("Status")]
        #
        self.__model = SimpleListModel(headers, self.items)
        self.tree_view.setModel(self.__model)
        self.tree_view.setColumnHidden(0, True)
        self.addWidget(self.tree_view)
        
        self.running = False

    @property
    def parent(self):
        return self.weak_parent()

    def clear_list(self):
        self.__model.clear()
        self.rows_buffer.clear()

    def store_items(self, item_list):
        for download_item in item_list:
            item = [download_item.id, download_item.name, None]
            self.__model.append(item)
            self.rows_buffer[item[0]] = item
        if not self.running:
            self.running = True
            self.timer = self.parent.idle_timeout(1000, self.update_)
    
    def update_(self):
        status = self.unrar.get_status()
        if status:
            id_item, complete, err_msg = status
            row = self.rows_buffer[id_item]
            if complete:
                row[2] = err_msg if err_msg else _("Success")
                self.__model.refresh()
        else:
            self.running = False
            self.timer.stop()