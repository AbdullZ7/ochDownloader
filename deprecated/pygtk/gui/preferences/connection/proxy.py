import gtk
import pygtk

import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
import core.cons as cons
from core.conf_parser import conf


class Proxy(gtk.Frame):  #gtk.VBox):
    """"""
    def __init__(self):
        """"""
        #connection-proxy
        #gtk.VBox.__init__(self, False)
        #self.set_border_width(10)
        gtk.Frame.__init__(self, _("Proxy:"))
        #frame_poxy = gtk.Frame("Proxy:")
        vbox_proxy = gtk.VBox(False, 10)
        hbox_proxy = gtk.HBox(False, 10)
        vbox_proxy.set_border_width(10) #outside-space
        
        #proxy choice-menu
        self.proxy_without =  gtk.RadioButton(group=None, label=_("Without proxy"))
        self.proxy_without.connect("toggled", self.on_proxy_toggle, hbox_proxy)
        self.proxy_http =  gtk.RadioButton(group=self.proxy_without, label=_("Manual proxy config"))
        self.proxy_http.connect("toggled", self.on_http_proxy_toggle, hbox_proxy)
        vbox_proxy.pack_start(self.proxy_without, False, False)
        vbox_proxy.pack_start(self.proxy_http, False, False)
        
        #proxy ip field
        label_http_proxy = gtk.Label(_("HTTP Proxy:"))
        hbox_proxy.pack_start(label_http_proxy, False, False)
        proxy_ip, proxy_port, proxy_type = conf.get_proxy()
        self.entry_proxy_ip = gtk.Entry()
        self.entry_proxy_ip.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.entry_proxy_ip.set_width_chars(25) #entry width
        self.entry_proxy_ip.set_text(proxy_ip)
        hbox_proxy.pack_start(self.entry_proxy_ip)
        #proxy port spin-field
        label_port = gtk.Label(_("Port:"))
        hbox_proxy.pack_start(label_port, False, False)
        self.spin_proxy_port = gtk.SpinButton(None, 1, 0)
        self.spin_proxy_port.set_property("shadow-type", gtk.SHADOW_NONE)
        self.spin_proxy_port.set_range(0, 100000)
        self.spin_proxy_port.set_increments(1, 1)
        self.spin_proxy_port.set_numeric(True)
        self.spin_proxy_port.set_value(proxy_port)
        hbox_proxy.pack_start(self.spin_proxy_port, False, False)
        hbox_proxy.set_sensitive(False)
        
        self.proxy_active_choice(hbox_proxy)
        
        vbox_proxy.pack_start(hbox_proxy, False, False)
        #frame_poxy.add(vbox_proxy)
        #self.pack_start(frame_poxy, False, False)
        self.add(vbox_proxy)

    def proxy_active_choice(self, hbox_proxy):
        """"""
        if conf.get_proxy_active():
            self.proxy_http.set_active(True)
            hbox_proxy.set_sensitive(True)
        else:
            self.proxy_without.set_active(True)

    def on_proxy_toggle(self, toggle, hbox_proxy):
        """"""
        if toggle.get_active(): #true si NO estaba activo.
            hbox_proxy.set_sensitive(False)

    def on_http_proxy_toggle(self, toggle, hbox_proxy):
        """"""
        if toggle.get_active(): #true si NO estaba activo.
            hbox_proxy.set_sensitive(True)

    def load(self):
        """"""
        pass

    def save(self): #for polymorphism
        """"""
        if self.proxy_http.get_active():
            conf.set_proxy_active("True")
        else:
            conf.set_proxy_active("False")
        proxy_ip, port, proxy_type = self.entry_proxy_ip.get_text(), str(self.spin_proxy_port.get_value_as_int()), cons.PROXY_HTTP
        conf.set_proxy(proxy_ip, port, proxy_type)



