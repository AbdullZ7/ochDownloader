import weakref
import logging
logger = logging.getLogger(__name__)

from core import cons
from core import utils
from core.api import api
from core.config import conf
from core.container import Container

from PySide.QtGui import *
from PySide.QtCore import *

import media
import signals
from list_model import SimpleListModel
from context_menu import Menu
from add_links_dlg import AddLinks
from generic_dialog import Dialog


class AddDownloads(QVBoxLayout):
    def __init__(self, parent):
        QVBoxLayout.__init__(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(5)

        self.weak_parent = weakref.ref(parent)
        
        self.tree_view = QTreeView()

        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.context_menu)

        #listview look
        self.tree_view.setWordWrap(True) #search textElideMode
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setIndentation(0)
        self.tree_view.setAlternatingRowColors(True)

        self.icons_dict = self.get_icons()
        self.items = []
        self.rows_buffer = {} #{id_item: row_obj, }

        bool_cols = [1, ]
        image_cols = [2, ]
        headers = ["hidden_id_item", "", "", _("File Name"), _("Host"), _("Size"), _("Status Message")]

        self.__model = SimpleListModel(headers, self.items, bool_cols, image_cols)
        self.tree_view.setModel(self.__model)
        self.addWidget(self.tree_view)

        self.tree_view.setColumnHidden(0, True)
        self.tree_view.setColumnWidth(1, 27)
        self.tree_view.setColumnWidth(2, 27)
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

        self.paths_list = conf.get_save_dl_paths()

        if not self.paths_list:
            self.cb.addItem(cons.DLFOLDER_PATH)
        else:
            [self.cb.addItem(path) for path in reversed(self.paths_list)]

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
        
        self.menu = QMenu()
        import_action = self.menu.addAction(_("Import Container"), self.on_import_container)
        self.menu.addSeparator()
        recheck_action = self.menu.addAction(_("Re-check"), self.on_recheck)
        clear_action = self.menu.addAction(_("Clear list"), self.on_clear_list)

        btn_menu = QPushButton()
        btn_menu.setMenu(self.menu)
        btn_menu.setFixedHeight(35)
        btn_menu.setMaximumWidth(22)
        btn_menu.setFlat(True)
        hbox.addWidget(btn_menu)
        
        self.addLayout(hbox)

        #custom signals
        signals.add_downloads_to_check.connect(self.add_downloads_to_check)
        
        #update list
        self.timer = parent.idle_timeout(1000, self.update_)

    @property
    def parent(self):
        return self.weak_parent()

    def get_selected_rows(self):
        """"""
        selected_rows = [index.row() for index in self.tree_view.selectionModel().selectedRows()]
        selected_rows.sort()
        return selected_rows

    def context_menu(self, position):
        rows = self.get_selected_rows()

        is_single_row = True if len(rows) == 1 else False

        options = [(_('Save as...'), self.on_save_as, is_single_row),
                    None,
                    (_('Download Selected'), self.on_download_selected, True),
                    None,
                    (_('Select all'), self.on_select_all, True),
                    (_('Select none'), self.on_select_none, True),
                    (_('Select inverse'), self.on_select_inverse, True),
                    None,
                    (_('Re-check'), self.on_recheck, True),
                    (_('Clear list'), self.on_clear_list, True)]

        menu = Menu(options)
        
        menu.exec_(self.tree_view.viewport().mapToGlobal(position))

    def on_save_as(self):
        rows = self.get_selected_rows()
        row = self.items[rows[0]]
        item_id = row[0]
        download_item = api.get_checking_download_item(item_id)
        widget = QLineEdit()

        # set the line entry file name if we have one.
        if download_item.save_as:
            widget.setText(download_item.save_as)
        elif download_item.name != cons.UNKNOWN:
            widget.setText(download_item.name)

        dialog = Dialog(self.parent, "Save as", widget)
        if dialog.result() == QDialog.Accepted:
            save_as = widget.text()
            # change the file name in treeview and DownloadItem
            if save_as:
                api.save_download_as(download_item, save_as)
                api.set_download_name(download_item, save_as)
                row[3] = save_as

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
                self.add_downloads_to_check(links_list, copy_link=False)
    
    def on_add_links(self):
        dialog = AddLinks(self.parent)
        result_code = dialog.result()
        links_list = dialog.links_list
        if result_code == QDialog.Accepted and links_list:
            self.add_downloads_to_check(links_list)
    
    def on_examine(self):
        folder = QFileDialog.getExistingDirectory()
        if folder:
            self.cb.setEditText(folder)
    
    def cb_remove(self, text):
        index = self.cb.findText(text)
        if index >= 0:
            self.cb.removeItem(index)
    
    def on_download_selected(self):
        # save the selected path
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

        # move selected items to downloads tab
        id_items_list = []
        iters = []

        for row in self.items:
            if row[1]:
                iters.append(row)
                id_item = row[0]
                id_items_list.append(id_item)
                del self.rows_buffer[id_item]

        [self.__model.remove(self.items.index(iter)) for iter in iters]
        
        item_list = api.pop_checking_items(id_items_list)
        for download_item in item_list:
            download_item.path = current_path

        signals.add_to_downloader.emit(item_list)

    def add_downloads_to_check(self, links_list, copy_link=True):
        for link in links_list:
            download_item = api.create_download_item(cons.UNKNOWN, link, copy_link=copy_link)
            api.add_to_checker(download_item)
            item = [download_item.id, True, self.icons_dict[cons.LINK_CHECKING], cons.UNKNOWN, None, None, None]
            #self.items.append(item)
            self.__model.append(item)
            self.rows_buffer[item[0]] = item
        api.start_checking()
    
    def update_(self):
        checking_downloads = api.get_checking_downloads()
        api.update_checking_downloads()
        for download_item in checking_downloads.itervalues():
            row = self.rows_buffer[download_item.id]
            if download_item.link_status == cons.LINK_DEAD:
                row[1] = False
            row[2] = self.icons_dict[download_item.link_status]
            row[3] = download_item.name
            if not download_item.host == cons.UNSUPPORTED:
                row[4] = download_item.host
            if download_item.size:
                row[5] = utils.size_format(download_item.size)
            row[6] = download_item.link_status_msg
        self.__model.refresh()

    def get_icons(self):
        alive = media.get_pixmap(media.ALIVE, media.SMALL)
        dead = media.get_pixmap(media.DEAD, media.SMALL)
        error = media.get_pixmap(media.ERROR, media.SMALL)
        checking = media.get_pixmap(media.CHECKING, media.SMALL)
        #unavailable = media.get_pixmap(media.ERROR, media.SMALL)

        return {cons.LINK_ALIVE: alive, cons.LINK_DEAD: dead,
                cons.LINK_UNAVAILABLE: error, cons.LINK_ERROR: error,
                cons.LINK_CHECKING: checking}