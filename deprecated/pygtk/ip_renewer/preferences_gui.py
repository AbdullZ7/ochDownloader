import sys
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import pygtk
import gtk
import gobject

from core.conf_parser import conf
import core.cons as cons

from gui.dialog_base import FileChooserDialog


#Config parser
OPTION_IP_RENEW_ACTIVE = "ip_renew_active"
OPTION_IP_RENEW_SCRIPT_PATH = "ip_renew_script_path"
OPTION_RENEW_SCRIPT_ACTIVE = "renew_script_active"


class Preferences(gtk.VBox):
    """"""
    def __init__(self):
        """"""
        gtk.VBox.__init__(self, False, 10)
        
        hbox_script = gtk.HBox(False, 10)
        
        #choice-menu
        self.renew_default =  gtk.RadioButton(group=None, label=_("IP Renew (default)"))
        self.renew_default.connect("toggled", self.on_renew_default_toggle, hbox_script)
        self.renew_script =  gtk.RadioButton(group=self.renew_default, label=_("Run Custom Script"))
        self.renew_script.connect("toggled", self.on_renew_script_toggle, hbox_script)
        self.pack_start(self.renew_default, False, False)
        self.pack_start(self.renew_script, False, False)
        
        #renew script field
        label_renew_script = gtk.Label(_("Path:"))
        hbox_script.pack_start(label_renew_script, False, False)
        self.entry_renew_script = gtk.Entry()
        self.entry_renew_script.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.entry_renew_script.set_width_chars(25) #entry width
        #
        self.entry_renew_script.set_text(conf.get_addon_option(OPTION_IP_RENEW_SCRIPT_PATH, default=""))
        hbox_script.pack_start(self.entry_renew_script)
        button = gtk.Button(_("Examine..."))
        button.set_size_request(80, 35)
        button.connect("clicked", self.on_examine)
        hbox_script.pack_start(button, False, False)
        hbox_script.set_sensitive(False)
        
        self.renew_active_choice(hbox_script)
        
        self.pack_start(hbox_script, False, False)
    
    def renew_active_choice(self, hbox_script):
        """"""
        if conf.get_addon_option(OPTION_RENEW_SCRIPT_ACTIVE, default=False, is_bool=True):
            self.renew_script.set_active(True)
            hbox_script.set_sensitive(True)
        else:
            self.renew_default.set_active(True)
    
    def on_renew_default_toggle(self, toggle, hbox_script):
        """"""
        if toggle.get_active(): #true si NO estaba activo.
            hbox_script.set_sensitive(False)
    
    def on_renew_script_toggle(self, toggle, hbox_script):
        """"""
        if toggle.get_active(): #true si NO estaba activo.
            hbox_script.set_sensitive(True)
    
    def on_examine(self, widget):
        """"""
        openfolder = FileChooserDialog(title=_("Open Folder"), action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        openfolder.set_default_response(gtk.RESPONSE_OK)
        response = openfolder.run()
        if response == gtk.RESPONSE_OK:
            self.entry_renew_script.set_text(openfolder.get_filename().decode(sys.getfilesystemencoding())) #("utf-8"))
        openfolder.destroy()
    
    def load(self):
        """"""
        pass
    
    def save(self):
        """"""
        if self.renew_script.get_active():
            conf.set_addon_option(OPTION_RENEW_SCRIPT_ACTIVE, "True")
        else:
            conf.set_addon_option(OPTION_RENEW_SCRIPT_ACTIVE, "False")
        ip_renew_script_path = self.entry_renew_script.get_text()
        conf.set_addon_option(OPTION_IP_RENEW_SCRIPT_PATH, ip_renew_script_path)
