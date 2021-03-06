import os
import weakref
import logging
logger = logging.getLogger(__name__)

from core import cons
from core import events
from core import utils
from core.config import conf
from core.api import api

from PySide.QtGui import *
from PySide.QtCore import *

import media
import signals
from list_model import SimpleListModel
from context_menu import Menu


class Downloads(QTreeView):
    def __init__(self, parent):
        #TODO: Create wrapper or subclass list to append and remove from items and rows_buffer.
        QTreeView.__init__(self)

        self.weak_parent = weakref.ref(parent)

        #listview look
        self.setWordWrap(True) #search textElideMode
        self.setRootIsDecorated(False)
        self.setIndentation(0)
        self.setAlternatingRowColors(True)
        
        self.icons_dict = self.get_icons()
        self.items = []
        self.rows_buffer = {} #{id_item: row_obj, }

        headers = ["hidden_id_item", "", _("File Name"), _("Host"), _("Size"), _("Complete"),
                   _("Progress"), _("Time"), _("Remain"), _("Speed"), _("Status Message")]
        
        self.__model = SimpleListModel(headers, self.items)
        self.setModel(self.__model)
        self.setColumnHidden(0, True)
        self.setColumnWidth(1, 27)
        self.header().setResizeMode(1, QHeaderView.Fixed)
        #self.header().setResizeMode(3, QHeaderView.ResizeToContents)
        
        self.im_delegate = ImageDelegate(self)
        self.setItemDelegateForColumn(1, self.im_delegate)
        
        self.im2_delegate = ImageDelegate(self)
        self.setItemDelegateForColumn(3, self.im2_delegate)
        
        self.nf_delegate = NoFocusDelegate(self)
        self.setItemDelegate(self.nf_delegate)
        
        self.pb_delegate = ProgressBarDelegate(self)
        self.setItemDelegateForColumn(6, self.pb_delegate)
        
        #see http://stackoverflow.com/questions/1987546/qt4-stylesheets-and-focus-rect for removing the drawed border on focus
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        #self.setDragEnabled(True)
        #self.setAcceptDrops(True)
        #self.setDropIndicatorShown(False)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        #self.setDefaultDropAction(Qt.MoveAction)
        
        #drop indicator
        self.line = QWidget(self.viewport())
        self.line.setAutoFillBackground(True)
        pal = self.line.palette()
        pal.setColor(self.line.backgroundRole(), Qt.black)
        self.line.setPalette(pal)
        self.line.setGeometry(0, 0, 0, 0)
        self.line.hide()

        #custom signals
        signals.add_to_downloader.connect(self.add_to_downloader)
        signals.on_stop_all.connect(self.on_stop_all)

        #update list
        self.timer = parent.idle_timeout(1000, self.update_)

    @property
    def parent(self):
        return self.weak_parent()

    def remove_row(self, id_item):
        item = self.rows_buffer.pop(id_item)
        self.__model.remove(self.items.index(item))
    
    def get_selected_rows(self):
        """"""
        selected_rows = [index.row() for index in self.selectionModel().selectedRows()]
        selected_rows.sort()
        return selected_rows
    
    def dragEnterEvent(self, event):
        #FIXME: weird things may happen if draggin when an item is removed or added.
        #event.setDropAction(Qt.MoveAction)
        event.accept()
    
    def dragMoveEvent(self, event): #paint drop indicator at the current position.
        q_index = self.indexAt(event.pos())
        
        if q_index.isValid():
            rect = self.visualRect(q_index)
            self.line.setGeometry(0, rect.top(), self.viewport().width(), 1)
        else:
            q_index = self.__model.index(self.__model.rowCount() - 1)
            rect = self.visualRect(q_index)
            self.line.setGeometry(0, rect.bottom(), self.viewport().width(), 1)
        
        self.line.show()
    
    def dragLeaveEvent(self, event): #out of the drop area.
        self.line.hide()
    
    def dropEvent(self, event):
        self.line.hide()
        
        q_index = self.indexAt(event.pos())
        if q_index.isValid():
            index = q_index.row()
        else:
            index = -1
        
        items = [self.items[row] for row in self.get_selected_rows()]
        dest_item = self.items[index]
        [self.__model.remove(self.items.index(item)) for item in items if item != dest_item]
        if index >= 0:
            index = self.items.index(dest_item)
            [self.__model.insert(index, item) for item in reversed(items) if item != dest_item]
        else:
            [self.__model.append(item) for item in items if item != dest_item]
        api.reorder_queue([row[0] for row in self.items])
    
    #def keyboard_event(self, widget, event):
        #if gtk.gdk.keyval_name(event.keyval) == "Delete": #supr. key
            #self.on_delete()
    
    def contextMenuEvent(self, event):
        rows = self.get_selected_rows()

        is_selection = True if rows else False

        options = [(_('Open destination folder'), self.on_open_folder, is_selection),
                    (_('Copy link'), self.on_copy_link, is_selection),
                    #(_('Add password'), self.on_password, is_selection),
                    None,
                    (_('Delete'), self.on_delete, is_selection),
                    None,
                    (_('Start all'), self.on_start_all, True),
                    (_('Stop all'), self.on_stop_all, True),
                    (_('Clear Completed'), self.on_clear_completed, True)]

        menu = Menu(options)
        
        menu.exec_(event.globalPos())

    def selectionChanged(self, selected, deselected):
        #overridden slot
        QTreeView.selectionChanged(self, selected, deselected)

        BTN = 0
        rows = self.get_selected_rows()

        if len(rows) == 1:  # single selection.
            row_index = rows[0]
            id_item = self.items[row_index][0]
            stopped_downloads = api.get_stopped_downloads()

            if id_item in stopped_downloads:
                self.parent.stop[BTN].setEnabled(False)
                self.parent.start[BTN].setEnabled(True)
            else:
                self.parent.stop[BTN].setEnabled(True)
                self.parent.start[BTN].setEnabled(False)
        elif rows:  # multi selection
            self.parent.stop[BTN].setEnabled(True)
            self.parent.start[BTN].setEnabled(True)
        else:  # no selection
            self.parent.stop[BTN].setEnabled(False)
            self.parent.start[BTN].setEnabled(False)
    
    def on_open_folder(self):
        rows = self.get_selected_rows()
        if rows:
            items_list = api.get_download_items([self.items[row_index][0] for row_index in rows])
            paths_list = {download_item.path for download_item in items_list}
            for folder_path in paths_list:
                utils.open_folder_window(folder_path)

    def on_copy_link(self):
        rows = self.get_selected_rows()
        if rows:
            items_list = api.get_download_items([self.items[row_index][0] for row_index in rows])
            links_list = [download_item.link for download_item in items_list if download_item.can_copy_link]
            clipboard = QApplication.clipboard()
            clipboard.setText('\n'.join(links_list))
    
    def on_password(self):
        rows = self.get_selected_rows()
        if rows:
            pass
            #entry = gtk.Entry()
            #entry.add_events(gtk.gdk.KEY_RELEASE_MASK)
            #entry.set_width_chars(25) #entry width
            
            #m = DlgGui(self.__parent, None, _("Password"), None, True, append_widget=entry)
            
            #pwd = entry.get_text().strip()
            
            #if m.accepted and pwd:
                #events.add_password.emit(pwd)
    
    def on_delete(self):
        rows = self.get_selected_rows()
        if rows:
            #message = _("Do you want to remove this download? (downloaded segments will be deleted)")
            #m = DlgGui(self.__parent, gtk.STOCK_DIALOG_WARNING, _("Remove Files"), message, True, True)
            m = True
            if m:
                id_items_list = []
                for row_index in rows:
                    id_item = self.items[row_index][0]
                    id_items_list.append(id_item)
                [self.remove_row(id_item) for id_item in id_items_list]
                api.delete_download(id_items_list)
    
    def on_clear_completed(self):
        finished_icon = self.icons_dict[cons.STATUS_FINISHED]
        for row in self.items[:]:
            if row[1] == finished_icon:
                self.remove_row(row[0])
        api.clear_complete()
    
    def on_start_all(self):
        """
        BUG: El boton start y stop no cambia.
        """
        id_item_list = [row[0] for row in self.items]
        api.start_all(id_item_list)
        stopped_icon = self.icons_dict[cons.STATUS_STOPPED]
        queue_icon = self.icons_dict[cons.STATUS_QUEUE]
        for row in self.items:
            if row[1] == stopped_icon:
                row[1] = queue_icon

    def on_stop_all(self):
        api.stop_all()
        stopped_icon = self.icons_dict[cons.STATUS_STOPPED]
        queue_icon = self.icons_dict[cons.STATUS_QUEUE]
        for row in self.items:
            if row[1] == queue_icon:
                row[1] = stopped_icon

    def add_to_downloader(self, download_items):
        for download_item in download_items:
            api.add_to_downloader(download_item)
            self.store_item(download_item)

        if conf.get_auto_switch_tab():
            signals.switch_tab.emit(0)

        api.next_download()

    def store_item(self, download_item):
        size_file = utils.size_format(download_item.size) if download_item.size else None
        size_complete = utils.size_format(download_item.size_complete) if download_item.size_complete else None
        time = utils.time_format(download_item.time) if download_item.time else None
        host_icon = self.get_host_icon(download_item.host)

        item = [download_item.id, self.icons_dict[download_item.status], download_item.name, [host_icon, None, None],
                size_file, size_complete, download_item.progress, time, None, None, download_item.status_msg]

        self.__model.append(item)
        self.rows_buffer[item[0]] = item

    def update_(self):
        active_downloads = api.get_active_downloads()
        api.update_active_downloads()
        for download_item in active_downloads.itervalues():
            row = self.rows_buffer[download_item.id]
            #row[0] = download_item.id
            row[1] = self.icons_dict[download_item.status]
            row[2] = download_item.name
            #row[3][0] = download_item.host
            row[3][1] = self.icons_dict[cons.DL_RESUME] if download_item.can_resume else None
            row[3][2] = self.icons_dict[cons.DL_PREMIUM] if download_item.is_premium else None
            row[4] = utils.size_format(download_item.size) if download_item.size else None
            row[5] = utils.size_format(download_item.size_complete) if download_item.size_complete else None
            row[6] = download_item.progress
            row[7] = utils.time_format(download_item.time) if download_item.time else None
            row[8] = utils.time_format(download_item.time_remain) if download_item.time_remain else None
            row[9] = utils.speed_format(download_item.speed) if download_item.speed else None
            row[10] = self.get_status_msg(download_item)
        self.__model.refresh()

    def get_status_msg(self, download_item):
        if download_item.fail_count:
            return "{0} ({1} #{2})".format(download_item.status_msg, _("Retry"), download_item.fail_count)
        else:
            return download_item.status_msg
    
    def get_host_icon(self, host):
        try:
            return self.icons_dict[host]
        except KeyError:
            self.icons_dict[host] = QPixmap(os.path.join(cons.PLUGINS_PATH, host.replace('.', '_'), "favicon.ico"))
            return self.icons_dict[host]
    
    def get_icons(self):
        running = media.get_pixmap(media.START, media.SMALL)
        stopped = media.get_pixmap(media.STOP, media.SMALL)
        queue = media.get_pixmap(media.QUEUE, media.SMALL)
        finished = media.get_pixmap(media.CHECK, media.SMALL)
        error = media.get_pixmap(media.X_MARK, media.SMALL)
        
        resume = media.get_pixmap(media.REFRESH, media.SMALL)
        premium = media.get_pixmap(media.ACCOUNTS, media.SMALL)
        
        return {cons.STATUS_RUNNING: running, cons.STATUS_STOPPED: stopped,
                cons.STATUS_QUEUE: queue, cons.STATUS_FINISHED: finished,
                cons.STATUS_ERROR: error, 
                cons.DL_RESUME: resume, cons.DL_PREMIUM: premium}


class NoFocusDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent)
    
    def paint(self, painter, option, index):
        if (option.state & QStyle.State_HasFocus):
            option.state ^= QStyle.State_HasFocus
        QStyledItemDelegate.paint(self, painter, option, index)


class ImageDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent)
    
    def sizeHint(self, option, index):
        return QSize(-1, 16)
    
    def paint(self, painter, option, index):
        
        if (option.state & QStyle.State_HasFocus):
            option.state ^= QStyle.State_HasFocus
        QStyledItemDelegate.paint(self, painter, option, index)
        
        painter.save()
        #rect = option.rect
        #rect = QRect(rect.left() + w_margin, rect.top() + h_margin, 16, 16) #center
        rect = option.rect
        width = 16 #rect.height()
        height = 16 #rect.height()
        #w_margin = max(0, rect.width() - width) / 2
        h_margin = max(0, rect.height() - height) / 2
        x = rect.left()
        y = rect.top() + h_margin
        margin = 2
        
        data = index.data() #pix (col 1) or list of pix (col 3)
        if data:
            if index.column() == 1:
                w_margin = max(0, rect.width() - width) / 2
                painter.drawPixmap(QRect(x + w_margin, y, width, height), data)
            else:
                for pix in data:
                    if pix is not None:
                        painter.drawPixmap(QRect(x, y, width, height), pix)
                        x += width + margin
        
        painter.restore()


class ProgressBarDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent=parent)

    #def sizeHint(self, option, index):
        #return QSize(-1, 26)
    
    def paint(self, painter, option, index):
        
        if (option.state & QStyle.State_HasFocus):
            option.state ^= QStyle.State_HasFocus
        QStyledItemDelegate.paint(self, painter, option, index)
        
        painter.save()
        #if not index.isValid():
            #return None
        #painter.save()
        #if index.column() == 2:
        #if option.state & QStyle.State_Selected: #paint background if selected.
            #painter.fillRect(option.rect, painter.brush())
        progress = index.data()
        bar_option = QStyleOptionProgressBarV2()
        bar_option.rect = option.rect
        bar_option.rect.setHeight(option.rect.height() - 1)
        bar_option.rect.setTop(option.rect.top() + 1)
        bar_option.minimum = 0
        bar_option.maximum = 100
        bar_option.progress = progress
        bar_option.text = str(progress) + '%'
        bar_option.textVisible = True
        bar_option.textAlignment = Qt.AlignCenter
        QApplication.style().drawControl(QStyle.CE_ProgressBar, bar_option, painter)
        
        
        
        #else:
            #QStyledItemDelegate.paint(self, painter, option, index)
        painter.restore()