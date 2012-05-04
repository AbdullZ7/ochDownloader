import gobject
import gtk

import Queue

from core.idle_queue import idle_loop


class DialogBase:
    def __init__(self):
        self.loop = gobject.MainLoop(is_running=True)
        self.__response = gtk.RESPONSE_NONE
    
    def run(self):
        """
        Mimic what run method does, according to the documentation.
        """
        self.show()
        self.set_modal(True)
        context = self.loop.get_context()
        while self.loop.is_running():
            try:
                callback = idle_loop.get_nowait()
                callback()
            except Queue.Empty:
                pass
            context.iteration(True)
        #self.set_modal(False)
        return self.__response
    
    def on_response(self, widget, id_response):
        self.__response = id_response
        self.loop.quit()
    
    def on_delete_event(self, widget, other=None):
        self.__response = gtk.RESPONSE_DELETE_EVENT
        self.loop.quit()
        return True #do not destroy it!
    
    def destroy(self):
        gtk.Dialog.destroy(self)
        self.loop.quit()
    
    def hide_all(self):
        gtk.Dialog.hide_all(self)
        self.loop.quit()
    
    def hide(self):
        gtk.Dialog.hide(self)
        self.loop.quit()


class Dialog(DialogBase, gtk.Dialog):
    def __init__(self, *args, **kwargs):
        DialogBase.__init__(self)
        gtk.Dialog.__init__(self, *args, **kwargs)
        self.connect("response", self.on_response)
        self.connect("delete-event", self.on_delete_event)


class AboutDialog(DialogBase, gtk.AboutDialog):
    def __init__(self, *args, **kwargs):
        DialogBase.__init__(self)
        gtk.AboutDialog.__init__(self, *args, **kwargs)
        self.connect("response", self.on_response)
        self.connect("delete-event", self.on_delete_event)


class FileChooserDialog(DialogBase, gtk.FileChooserDialog):
    def __init__(self, *args, **kwargs):
        DialogBase.__init__(self)
        gtk.FileChooserDialog.__init__(self, *args, **kwargs)
        self.connect("response", self.on_response)
        self.connect("delete-event", self.on_delete_event)

