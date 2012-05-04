import threading

import gtk
import gobject

import core.cons as cons

import gui.main_loop as main_loop
from dialog_base import Dialog


class DlgGui(Dialog):
    """"""
    def __init__(self, parent, severity_icon, title, message, accept=False, cancel=True, ask=False, append_widget=None):
        """"""
        Dialog.__init__(self)
        self.set_title(title)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(False)
        self.set_transient_for(parent)
        #self.vbox.set_spacing(0)
        #self.vbox.set_homogeneous(False)
        
        self.accepted = False
        self.append_widget = append_widget
        
        self.hbox = gtk.HBox()
        
        #aspect = gtk.AspectFrame()
        #hbox.pack_start(aspect, True, True, 10)
        #aspect.set_shadow_type(gtk.SHADOW_NONE)
        
        if severity_icon is not None:
            self.hbox.pack_start(gtk.image_new_from_stock(severity_icon, gtk.ICON_SIZE_DIALOG), padding=10)
            self.set_icon(self.render_icon(severity_icon, gtk.ICON_SIZE_MENU))
        
        if message is not None:
            self.label = gtk.Label(message)
            #self.label.set_width_chars(35)
            self.label.set_line_wrap(True)
            self.hbox.pack_start(self.label, padding=10)
        
        if append_widget is not None:
            self.hbox.pack_start(append_widget, True, True, 20)
        
        if cancel:
            stock_item = gtk.STOCK_NO if ask else gtk.STOCK_CANCEL
            close_btn = gtk.Button(None, stock_item)
            self.action_area.pack_start(close_btn)
            close_btn.connect("clicked", self.close)
        if accept:
            stock_item = gtk.STOCK_YES if ask else gtk.STOCK_OK
            ok_btn = gtk.Button(None, stock_item)
            self.action_area.pack_start(ok_btn)
            ok_btn.connect("clicked", self.accept)
        
        self.connect("response", self.close)
        
        self.vbox.pack_start(self.hbox, True, True, 20)
        
        self.show_all()
        self.run()
    
    def accept(self, button):
        """"""
        self.accepted = True
        self.close()

    def close(self, widget=None, other=None):
        """"""
        #self.hide_all()
        if self.append_widget is not None:
            self.hbox.remove(self.append_widget) #so it wont be destroyed.
        self.destroy()


if __name__ == "__main__":
    #DlgGui(None, gtk.STOCK_DIALOG_WARNING, "Manual Update Required", "some message large text some message large text some message large text some message large text")
    #frame = gtk.Frame("Password")
    entry = gtk.Entry()
    entry.add_events(gtk.gdk.KEY_RELEASE_MASK)
    entry.set_width_chars(25) #entry width
    #frame.add(entry)
    
    DlgGui(None, None, "Password", None, True, append_widget=entry)
    gtk.main()





