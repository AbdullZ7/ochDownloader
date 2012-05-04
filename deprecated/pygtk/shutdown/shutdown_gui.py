import pygtk
import gtk
import gobject

from shutdown import Shutdown
import core.cons as cons
from core.events import events

if cons.OS_WIN:
    from gui.misc import flash_wnd
from gui.dialog_base import Dialog

TIME_OUT = 60


class ShutdownDlg(Dialog):
    """"""
    def __init__(self, parent):
        """"""
        Dialog.__init__(self)
        self.set_transient_for(parent)
        self.set_icon(self.render_icon(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_MENU))
        self.set_title("Shutting down")
        self.set_size_request(340, 200)
        
        #self.quit = quit
        self.timeout = TIME_OUT
        self.cancel = False
        
        shut_label = gtk.Label(_("The system is going to shout down."))
        self.vbox.pack_start(shut_label, False, False, 10)
        
        self.label = gtk.Label(_("Shutting in") + " {0}".format(self.timeout))
        self.vbox.pack_start(self.label, False, False, 10)
        
        button = gtk.Button(None, gtk.STOCK_CANCEL)
        self.action_area.pack_start(button)
        button.connect("clicked", self.on_close)
        
        self.connect("response", self.on_close)
        
        gobject.timeout_add(1000, self.check_timeout)
        
        #Flash if the window is in the background.
        if cons.OS_WIN:
            flash_wnd.flash_taskbar_icon(parent.window.handle)
        
        self.show_all()
        self.run()
    
    def check_timeout(self):
        if self.cancel:
            return False
        elif self.timeout > 0:
            self.timeout -= 1
            self.label.set_text(_("Shutting in") + " {0}".format(self.timeout))
            return True
        else:
            shutdown = Shutdown()
            if shutdown.start_shutting():
                #self.quit()
                events.trigger_quit()
            return False
    
    def on_close(self, widget=None, other=None):
        """"""
        self.cancel = True
        self.destroy()

