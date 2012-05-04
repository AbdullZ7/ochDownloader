import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import pygtk
import gtk
import gobject

import core.cons as cons
from core.api import api

if cons.OS_WIN:
    from gui.misc import flash_wnd
from gui.dialog_base import Dialog


TIMEOUT = 55


class CaptchaDlg(Dialog):
    """"""
    def __init__(self, service, get_captcha, parent):
        """"""
        Dialog.__init__(self)
        #self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_transient_for(parent)
        self.set_icon(self.render_icon(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_MENU))
        self.set_title("{service_name} captcha".format(service_name=service))
        self.set_size_request(340, 200)
        
        self.get_captcha = get_captcha
        self.solution = None
        self.timeout = TIMEOUT
        self.cancel = False
        
        self.image = gtk.Image()
        self.vbox.pack_start(self.image)
        
        hbox = gtk.HBox()
        self.vbox.pack_start(hbox, False, False, 10)
        self.label = gtk.Label(_("Expires in") + " {0}".format(self.timeout))
        hbox.pack_start(self.label, True, True, 5)
        
        self.entry = gtk.Entry()
        hbox.pack_start(self.entry, False, False, 10)
        self.entry.set_width_chars(24)
        self.entry.set_max_length(40)
        self.entry.set_activates_default(True)
        self.entry.connect("activate", self.solve_captcha)
        
        button = gtk.Button(None, gtk.STOCK_CANCEL)
        self.action_area.pack_start(button)
        self.action_area.set_child_secondary(button, True) #left align.
        button.connect("clicked", self.on_cancel, parent)
        button = gtk.Button(None, gtk.STOCK_REFRESH)
        self.action_area.pack_start(button)
        button.connect("clicked", self.new_captcha)
        button = gtk.Button(None, gtk.STOCK_OK)
        self.action_area.pack_start(button)
        button.connect("clicked", self.solve_captcha)
        
        self.connect("response", self.on_close)
        
        self.new_captcha()
        gobject.timeout_add(1000, self.check_timeout)
        
        #Flash if the window is in the background.
        if cons.OS_WIN:
            flash_wnd.flash_taskbar_icon(parent.window.handle)

        self.show_all()
        self.run()
    
    def get_solution(self):
        """"""
        return self.solution
    
    def solve_captcha(self, widget=None):
        """"""
        tmp = self.entry.get_text()
        if tmp:
            self.solution = tmp.strip()
        self.on_close()

    def check_timeout(self):
        if self.cancel:
            return False
        elif self.timeout > 0:
            self.timeout -= 1
            self.label.set_text(_("Expires in") + " {0}".format(self.timeout))
            return True
        else:
            self.on_close()
            return False
    
    def new_captcha(self, widget=None):
        self.timeout = TIMEOUT
        self.solution = None
        img_type, img_data = self.get_captcha()
        if img_data:
            loader = gtk.gdk.PixbufLoader(img_type)
            loader.write(img_data)
            loader.close()
            self.image.set_from_pixbuf(loader.get_pixbuf())
        else:
            self.image.set_from_pixbuf(self.render_icon(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG))
        self.entry.set_text("")
        self.set_focus(self.entry)
    
    def on_cancel(self, widget, parent):
        """"""
        filter_host = [download_item.host for download_item in api.get_active_downloads().itervalues()
                            if download_item.time > 0]
        filter_id_items = [id_item for id_item, downloader_item in api.get_queue_downloads().iteritems()
                                    if download_item.host in filter_host]
        self.pending_events()
        api.stop_all(filter_host)
        self.pending_events()
        rows_buffer = parent.downloads_list_gui.rows_buffer
        stopped_icon = parent.downloads_list_gui.icons_dict[cons.STATUS_STOPPED]
        queue_icon = parent.downloads_list_gui.icons_dict[cons.STATUS_QUEUE]
        for id_item, row in rows_buffer.items():
            if row[1] == queue_icon and id_item not in filter_id_items:
                row[1] = stopped_icon
        self.on_close()
    
    def on_close(self, widget=None, other=None):
        """"""
        self.cancel = True
        self.destroy()
    
    def pending_events(self):
        """
        Avoid gui hanging.
        """
        while gtk.events_pending():
            gtk.main_iteration(False)
