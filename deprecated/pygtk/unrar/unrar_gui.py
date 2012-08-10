import re
import os
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import pygtk
import gtk
import gobject

import core.cons as cons
from core.conf_parser import conf
from core.api import api

from unrar import UnRAR


COMPLETE, ERR_MSG = range(2)


class UnRARGUI:
    """"""
    def __init__(self, event, download_item, parent, widgets_list):
        """"""
        self.download_item = download_item
        self.parent = parent
        self.event = event
        self.widgets_list = widgets_list
        
        self.hbox = gtk.HBox()
        
        self.unrar = UnRAR()
        self.is_extracting = False
        
        dest_path = self.download_item.path
        
        NAME, PART, EXT = range(3)
        pattern = "^(.*?)(\.part\d+)?(\.rar|\.r\d+)$" #capture name
        m = re.match(pattern, self.download_item.name)
        if m is not None: #is rar file
            m_tuple = m.groups()
            if not self.has_segments_left(m_tuple[NAME], pattern): #not segment left.
                if m_tuple[PART] is not None: #new ext. style
                    file_name = "".join((m_tuple[NAME], ".part1.rar"))
                else: #single part or old ext. style
                    file_name = "".join((m_tuple[NAME], ".rar"))
                
                file_path = os.path.join(self.download_item.path, file_name)
                th_id = self.unrar.add(file_path, dest_path)
                self.add_msg_box(th_id)
                self.is_extracting = True

    def add_msg_box(self, th_id):
        """"""
        [frame.hide_all() for frame in self.widgets_list]
        
        frame = gtk.Frame(label=None)
        halign1 = gtk.Alignment(0, 0, 0, 0) #left
        halign2 = gtk.Alignment(1, 0, 0, 0) #left
        
        hbox = gtk.HBox(False, 20)
        label = gtk.Label(_("Extracting:") + " " + self.download_item.name)
        hbox.pack_start(label)
        status_label = gtk.Label("(" + _("Running") + ")")
        hbox.pack_start(status_label)
        
        halign1.add(hbox)
        
        #get a stock close button image
        close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        image_w, image_h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        
        #make the close button
        btn = gtk.Button()
        btn.set_relief(gtk.RELIEF_NONE)
        btn.set_focus_on_click(False)
        btn.add(close_image)
        btn.set_size_request(image_w + 4, image_h + 4)

        #this reduces the size of the button
        style = gtk.RcStyle()
        style.xthickness = 0
        style.ythickness = 0
        btn.modify_style(style)
        
        btn.connect('clicked', self.on_close_button, frame)
        
        halign2.add(btn)
        
        hbox3 = gtk.HBox()
        hbox3.pack_start(halign1)
        hbox3.pack_start(halign2)
        frame.add(hbox3)
        
        self.widgets_list.append(frame)
        
        self.parent.vbox2.pack_start(frame, False, False)
        
        frame.show_all()
        btn.hide() #close btn
        
        gobject.timeout_add(1000, self.update_status, th_id, frame, btn, status_label)
    
    def update_status(self, th_id, frame, close_btn, status_label):
        """"""
        status_tuple = self.unrar.get_status(th_id)
        if status_tuple is not None:
            if status_tuple[COMPLETE]:
                if status_tuple[ERR_MSG] is None:
                    self.widgets_list.remove(frame)
                    frame.hide_all()
                    frame.destroy()
                    if self.widgets_list:
                        self.widgets_list[0].show_all()
                else:
                    status_label.set_text("(" + status_tuple[ERR_MSG] + ")")
                    close_btn.show() #show close button
                self.event.set()
                return False
        return True
    
    def on_close_button(self, widget, frame):
        """"""
        self.widgets_list.remove(frame)
        frame.hide_all()
        frame.destroy()
        if self.widgets_list:
            frame = self.widgets_list[0]
            frame.show_all()
    
    def has_segments_left(self, name, pattern):
        """"""
        NAME, PART, EXT = range(3)
        for download_item in api.get_active_downloads().values() + api.get_queue_downloads().values() + api.get_stopped_downloads().values():
            match_name = re.match(pattern, download_item.name)
            if match_name is not None:
                if name == match_name.groups()[NAME]:
                    return True
        return False


if __name__ == "__main__":
    pass
    
    
    
    
