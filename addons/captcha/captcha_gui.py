import weakref
import logging
logger = logging.getLogger(__name__)

import core.cons as cons
from core.api import api

from PySide.QtGui import *
from PySide.QtCore import *

if cons.OS_WIN:
    from qt.misc import flash_wnd
else:
    flash_wnd = None

TIMEOUT = 55


class CaptchaDialog(QDialog):
    """"""
    def __init__(self, host, get_captcha, parent):
        """"""
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        #self.set_icon(self.render_icon(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_MENU))
        self.setWindowTitle("{host} captcha".format(host=host))
        self.resize(340, 200)

        self.weak_parent = weakref.ref(parent)
        self.host = host
        self.get_captcha = get_captcha
        self.solution = None
        self.timeout = TIMEOUT
        
        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        self.setLayout(vbox)
        
        #captcha image
        #self.image = QPixmap()
        self.label = QLabel()
        self.load_image()
        #self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #self.label.setPixmap(self.image)
        vbox.addWidget(self.label)
        
        #input
        hbox_input = QHBoxLayout()
        vbox.addLayout(hbox_input)
        
        self.label_expires = QLabel("{} {}".format(_("Expires in"), self.timeout))
        hbox_input.addWidget(self.label_expires)
        
        self.entry_input = QLineEdit()
        hbox_input.addWidget(self.entry_input)
        
        #buttons
        vbox.addStretch()
        
        hbox_btns = QHBoxLayout()
        vbox.addLayout(hbox_btns)
        
        btn_cancel = QPushButton(_('Cancel'))
        btn_cancel.clicked.connect(self.on_cancel)
        btn_cancel.setFixedHeight(35)
        btn_cancel.setMaximumWidth(80)
        hbox_btns.addWidget(btn_cancel)
        
        hbox_btns.addStretch()
        
        btn_refresh = QPushButton(_('Refresh'))
        btn_refresh.clicked.connect(self.on_refresh)
        btn_refresh.setFixedHeight(35)
        btn_refresh.setMaximumWidth(80)
        hbox_btns.addWidget(btn_refresh)
        
        btn_ok = QPushButton(_('OK'))
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.on_ok)
        btn_ok.setFixedHeight(35)
        btn_ok.setMaximumWidth(80)
        hbox_btns.addWidget(btn_ok)
        
        #expires update
        self.timer = parent.idle_timeout(1000, self.expire_update)
        
        #note: if does not work, use singleShot timer.
        self.entry_input.setFocus() #call after creating all of the other widgets.

        #Flash if the window is in the background.
        if flash_wnd is not None:
            flash_wnd.flash_taskbar_icon(parent.winId())
        
        self.exec_()
        self.deleteLater()

    @property
    def parent(self):
        return self.weak_parent()

    def get_solution(self):
        return self.solution

    def on_ok(self):
        tmp = self.entry_input.text()
        if tmp:
            self.solution = tmp.strip()
        self.accept()
    
    def on_refresh(self):
        self.timeout = TIMEOUT
        self.solution = None
        self.load_image()
        self.entry_input.setText("")
        #self.set_focus(self.entry)
    
    def load_image(self):
        img_type, img_data = self.get_captcha()
        if img_data:
            image = QPixmap()
            image.loadFromData(img_data)
            self.label.setPixmap(image)
        else:
            self.label.setPixmap(QPixmap())
            #self.image.set_from_pixbuf(self.render_icon(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG))
    
    def expire_update(self):
        if self.timeout > 0:
            self.timeout -= 1
            self.label_expires.setText("{} {}".format(_("Expires in"), self.timeout))
        else:
            self.reject()
    
    def on_cancel(self):
        id_item_list = []
        # stop all downloads from this host
        for id_item, download_item in api.get_active_downloads().iteritems():
            if download_item.host == self.host and not download_item.start_time:
                api.stop_download(id_item)
                id_item_list.append(id_item)
        for id_item, download_item in api.get_queue_downloads().iteritems():
            if download_item.host == self.host:
                api.stop_download(id_item)
                id_item_list.append(id_item)
        # change queue icon to stopped
        for id_item in id_item_list:
            row = self.parent.downloads.rows_buffer[id_item]
            if row[1] == self.parent.downloads.icons_dict[cons.STATUS_QUEUE]:
                row[1] = self.parent.downloads.icons_dict[cons.STATUS_STOPPED]
        self.reject()
    
    def accept(self, *args, **kwargs):
        self.timer.stop()
        self.hide()
        QDialog.accept(self, *args, **kwargs)
    
    def reject(self, *args, **kwargs):
        self.timer.stop()
        self.hide()
        QDialog.reject(self, *args, **kwargs)
