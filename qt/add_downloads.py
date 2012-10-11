import threading
import os #clase SaveFile
import sys
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from core import cons
from core import misc
from core.api import api
from core.conf_parser import conf
from core.Container_Extractor import Container

from PySide.QtGui import *
from PySide.QtCore import *

import media
from list_model import SimpleListModel
from add_links_dlg import AddLinks


class AddDownloads(QVBoxLayout):
    def __init__(self, downloads, parent=None):
        QVBoxLayout.__init__(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(5)
        
        self.downloads = downloads
        self.parent = parent
        
        self.tree_view = QTreeView(parent)
        #
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.context_menu)
        #
        #listview look
        self.tree_view.setWordWrap(True) #search textElideMode
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setIndentation(0)
        self.tree_view.setAlternatingRowColors(True)
        #
        self.items = []
        self.rows_buffer = {} #{id_item: row_obj, }
        #self.items = [[True, "1", "11", "t5est", "t3est"], [True, "1", "11", "t5est", "t3est"], [True, "1", "11", "t5est", "t3est"]]
        bool_cols = [1, ]
        headers = ["hidden_id_item", "", _("Status"), _("File Name"), _("Host"), _("Size"), _("Status Message")]
        #
        self.__model = SimpleListModel(headers, self.items, bool_cols)
        self.tree_view.setModel(self.__model)
        self.addWidget(self.tree_view)
        #
        self.tree_view.setColumnHidden(0, True)
        self.tree_view.setColumnWidth(1, 27)
        self.tree_view.header().setResizeMode(1, QHeaderView.Fixed)
        
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(10)
        
        self.cb = QComboBox()
        #self.cb.setFixedWidth(100)
        self.cb.setEditable(True)
        self.cb.setFixedHeight(35)
        self.cb.setMinimumWidth(1)
        cb_view = self.cb.view()
        cb_view.setAlternatingRowColors(True)
        #
        self.paths_list = conf.get_save_dl_paths()
        if not self.paths_list:
            self.cb.addItem(cons.DLFOLDER_PATH)
        else:
            [self.cb.addItem(path) for path in reversed(self.paths_list)]
        #
        hbox.addWidget(self.cb)
        
        btn_examine = QPushButton('...')
        btn_examine.clicked.connect(self.on_examine)
        btn_examine.setFixedHeight(35)
        btn_examine.setMaximumWidth(80)
        hbox.addWidget(btn_examine)
        
        hbox.addSpacing(40) #index, size
        
        btn_download = QPushButton()
        btn_download.setIcon(media.get_icon(media.DOWN, media.MEDIUM))
        btn_download.setIconSize(QSize(24, 24))
        btn_download.clicked.connect(self.on_download_selected)
        btn_download.setFixedHeight(35)
        btn_download.setMaximumWidth(40)
        hbox.addWidget(btn_download)
        
        btn_add = QPushButton()
        btn_add.setIcon(media.get_icon(media.ADD, media.MEDIUM))
        btn_add.setIconSize(QSize(24, 24))
        btn_add.clicked.connect(self.on_add_links)
        btn_add.setFixedHeight(35)
        btn_add.setMaximumWidth(40)
        hbox.addWidget(btn_add)
        
        self.menu = QMenu(parent)
        import_action = self.menu.addAction(_("Import Container"), self.on_import_container)
        self.menu.addSeparator()
        recheck_action = self.menu.addAction(_("Re-check"), self.on_recheck)
        clear_action = self.menu.addAction(_("Clear list"), self.on_clear_list)
        #
        btn_menu = QPushButton()
        btn_menu.setMenu(self.menu)
        btn_menu.setFixedHeight(35)
        btn_menu.setMaximumWidth(22)
        btn_menu.setFlat(True)
        hbox.addWidget(btn_menu)
        
        
        self.addLayout(hbox)
        
        #update list
        parent.idle_timeout(1000, self.update)
    
    def context_menu(self, position):
        menu = QMenu()
        #indexes = self.selectedIndexes()
        
        #sensitive = True if indexes else False
        
        #individual_items = [('Open destination folder', self.on_open_folder),]
        
        #[menu.addAction(title, callback).setEnabled(sensitive) for title, callback in individual_items]

        #menu.addSeparator()
        
        generic_items = [(_('Download Selected'), self.on_download_selected),
                        (None, None),
                        (_('Select all'), self.on_select_all),
                        (_('Select none'), self.on_select_none),
                        (_('Select inverse'), self.on_select_inverse),
                        (None, None),
                        (_('Re-check'), self.on_recheck),
                        (_('Clear list'), self.on_clear_list)]
        
        [menu.addAction(title, callback) if title is not None else menu.addSeparator()
        for title, callback in generic_items]
        
        menu.exec_(self.tree_view.viewport().mapToGlobal(position))
    
    def on_clear_list(self):
        self.__model.clear()
        self.rows_buffer.clear()
        api.clear_pending()
    
    def on_recheck(self):
        api.recheck_items()

    def on_select_all(self):
        for row in self.items:
            row[1] = True

    def on_select_none(self):
        for row in self.items:
            row[1] = False

    def on_select_inverse(self):
        for row in self.items:
            row[1] = False if row[1] else True
    
    def on_import_container(self):
        file_name, filter = QFileDialog.getOpenFileName(filter='OCH Files (*.och)')
        if file_name:
            container = Container(file_name)
            container.extract_links()
            links_list = container.get_linklist()
            
            if links_list:
                self.links_checking(links_list, copy_link=False)
    
    def on_add_links(self):
        add_links = AddLinks(self.parent)
        result_code = add_links.result()
        links_list = add_links.links_list
        if result_code == QDialog.Accepted and links_list:
            self.links_checking(links_list)
    
    def on_examine(self):
        folder = QFileDialog.getExistingDirectory()
        if folder:
            self.cb.setEditText(folder)
    
    def cb_remove(self, text):
        index = self.cb.findText(text)
        if index >= 0:
            self.cb.removeItem(index)
    
    def on_download_selected(self):
        current_path = self.cb.currentText()
        self.cb_remove(current_path)
        self.cb.insertItem(0, current_path)
        if current_path in self.paths_list:
            self.paths_list.remove(current_path)
        self.paths_list.append(current_path)
        if len(self.paths_list) > 5:
            self.paths_list.pop(0)
            self.cb.removeItem(5)
        self.cb.setCurrentIndex(0)
        conf.set_save_dl_paths(self.paths_list)
        
        id_items_list = []
        iters = []
        for row in self.items:
            if row[1]: # and row[4] != cons.UNSUPPORTED: #tmp
                iters.append(row)
                id_item = row[0]
                id_items_list.append(id_item)
                del self.rows_buffer[id_item]
        [self.__model.remove(self.items.index(iter)) for iter in iters]
        
        item_list = api.get_added_items(id_items_list)
        
        api.downloader_init(item_list, current_path) #iniciar threads de descarga.
        #TODO: use a signal.
        self.downloads.store_items(item_list)

    def links_checking(self, links_list, copy_link=True):
        for link in links_list:
            download_item = api.create_download_item(cons.UNKNOWN, 0, link, copy_link) #return download_item object
            item = [download_item.id, True, cons.LINK_CHECKING, cons.UNKNOWN, None, None, None]
            #self.items.append(item)
            self.__model.append(item)
            self.rows_buffer[item[0]] = item
        api.start_checking()
    
    def update(self):
        checking_downloads = api.get_checking_downloads()
        api.update_checking_downloads()
        for download_item in checking_downloads.itervalues():
            try:
                row = self.rows_buffer[download_item.id]
                row[1] = True if download_item.link_status != cons.LINK_DEAD else False
                row[2] = download_item.link_status
                row[3] = download_item.name
                row[4] = download_item.host
                row[5] = misc.size_format(download_item.size)
                row[6] = download_item.link_status_msg
            except KeyError as err:
                logger.debug(err)
        self.__model.refresh()




