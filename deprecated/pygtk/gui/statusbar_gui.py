import gtk
import gobject

import os

import core.cons as cons
from core.api import api

from dlg_gui import DlgGui #Dialog

DEFAULT_SLOTS = 3


class StatusBar(gtk.Statusbar):
    """"""
    def __init__(self, add_Downloads_gui):
        """"""
        gtk.Statusbar.__init__(self)
        
        self.update_manager = api.start_update_manager()
        self.add_Downloads_gui = add_Downloads_gui
        
        hbox = gtk.HBox(False, 10)
        
        #Slots limit
        label_slots = gtk.Label(_("Slots limit:"))
        hbox.pack_start(label_slots, False, False)
        self.max_slots = gtk.SpinButton(None, 1, 0)
        self.max_slots.set_property("shadow-type", gtk.SHADOW_NONE)
        self.max_slots.set_range(1, 20)
        self.max_slots.set_increments(1, 1)
        self.max_slots.set_value(DEFAULT_SLOTS)
        self.max_slots.set_numeric(True)
        api.new_slot_limit(DEFAULT_SLOTS)
        #self.max_speed.set_value()
        hbox.pack_start(self.max_slots, False, False)
        
        self.max_slots.connect("value-changed", self.change_slots)
        
        #Speed limit
        label_speed = gtk.Label(_("Speed limit:"))
        hbox.pack_start(label_speed, False, False)
        self.max_speed = gtk.SpinButton(None, 4, 0)
        self.max_speed.set_property("shadow-type", gtk.SHADOW_NONE)
        self.max_speed.set_range(0, 5000)
        self.max_speed.set_increments(10, 0)
        self.max_speed.set_numeric(True)
        #self.max_speed.set_value()
        hbox.pack_start(self.max_speed, False, False)
        
        self.max_speed.connect("value-changed", self.change_speed)
        
        
        self.pack_start(hbox, False, False)
        
        #update check.
        self.msg_id = self.push_msg(_("Update checking...")) #push(id, message)
        gobject.timeout_add(2000, self.update_check) #auto actualizar status cada 1 seg.
        
        self.show_all()

    def push_msg(self, msg):
        """"""
        msg_id = self.push(1, msg) #context_id=1
        return msg_id

    def pop_msg(self, msg_id):
        """"""
        self.remove_message(1, msg_id) #context_id=1

    def change_slots(self, spinbutton):
        """"""
        limit = spinbutton.get_value_as_int()
        api.new_slot_limit(limit)

    def change_speed(self, spinbutton):
        """"""
        limit = spinbutton.get_value_as_int()
        if limit < 10 and limit != 0:
            limit = 10
            spinbutton.set_value(10)
        api.bucket.rate_limit(limit)
    
    def update_check(self):
        """
        TODO: implementar algun dia, cuando tenga ftp propio.
        if self.update_manager.manual_update:
                    message = "You cannot perform an automatic update, this time.\nPlease download the latest version from: www.ochdownloader.com"
                    m = DlgGui(None, gtk.STOCK_DIALOG_WARNING, "Manual Update Required", message)
                elif os.path.exists(cons.UPDATE_PATH):
                    #TODO: get direct link, self.update_manager.url_update
                    message = "There is an update available. Do you want to download it now?"
                    m = DlgGui(None, gtk.STOCK_DIALOG_WARNING, "Update Available", message, True, True)
                    if m.accepted:
                        os.popen("{0} -p {1} -a {2} -m {3} -u {4} --flagrun".format(cons.UPDATE_PATH, cons.DLFOLDER_PATH, cons.APP_PATH, self.update_manager.fhash_update, self.update_manager.url_update))
                else:
                    message = "The update application is missing.\nPlease download the latest version from: www.ochdownloader.com"
                    m = DlgGui(None, gtk.STOCK_DIALOG_WARNING, "Manual Update Required", message)
        """
        if self.update_manager.update_check_complete:
            if self.update_manager.update_available:
                self.pop_msg(self.msg_id) #eliminar mensaje anterior, sino se acumulan.
                self.push_msg(_("Update available"))
                #add links to check list.
                self.add_Downloads_gui.checking_links(self.update_manager.url_update)
            else:
                self.pop_msg(self.msg_id)
            return False #stop the gobject update
        return True
