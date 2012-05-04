import gtk
import gobject

import threading
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
from core.misc import tail, smartdecode #read file from bottom.

from dialog_base import Dialog


class Log(gtk.VBox):
    """"""
    def __init__(self):
        gtk.VBox.__init__(self)
        
        self.set_homogeneous(False)
        self.set_spacing(10) #espacio vertical entre hijos.
        self.set_border_width(0) #outside-space
        
        self.text_field = gtk.TextView()
        self.text_field.set_editable(False)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        scroll.add(self.text_field)

        self.pack_start(scroll)
        # ----
        hbox = gtk.HBox(False, 10) #view full log button
        #gtk.HBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio horizontal entre hijos.

        self.button1 = gtk.Button(_("View Full Log"))
        self.button1.set_size_request(180, 35)
        self.button1.connect("clicked", self.on_view_log)
        hbox.add(self.button1)
        
        halign1 = gtk.Alignment(0, 0, 0, 0) #horizontal container. left liagment.
        #xalign: espacio libre a la izquierda del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        #yalign: espacio libre vertical arriba del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        halign1.add(hbox)
        
        self.pack_start(halign1, False) #pack_start(child, expand=True, fill=True, padding=0)
    
    def on_load(self):
        """
        load the last few lines of the file.log
        This method is suppose to be called on switch-tab event (main_gui)
        """
        try:
            with open(cons.LOG_FILE, "rb", cons.FILE_BUFSIZE) as fh:
                last_lines = tail(fh) #misc function
        except EnvironmentError as err:
            last_lines = str(err)
            logger.warning("{0}".format(err))
        
        buffer = self.text_field.get_buffer()
        buffer.set_text(smartdecode(last_lines))

    def on_view_log(self, widget, other=None):
        """"""
        ViewFullLog()
    
    
class ViewFullLog(Dialog):
    """"""
    def __init__(self):
        """"""
        Dialog.__init__(self)
        self.set_title(_("Full Log File"))
        self.set_size_request(500, 330)
        
        #containers-separators.
        #self.vbox no puede ser cambiado en gtk.Dialog. Crear variable vbox y luego meterla en self.vbox.
        vbox1 = gtk.VBox(False, 20) #gtk.VBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio vertical entre hijos.
        vbox1.set_border_width(10) #outside-space
        
        #vbox1_start
        #Servers dropdown menu (ComboBox).
        #-------------------------------------------
        #frame1
        frame = gtk.Frame(_("Activity Log:"))
        
        self.text_field = gtk.TextView()
        self.text_field.set_editable(False)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_border_width(10)
        
        #arma el cuadro con los items
        scroll.add(self.text_field)
        
        frame.add(scroll)
        vbox1.pack_start(frame)
        #vbox.pack_start(child, expand=True, fill=True, padding=0) #padding = vertical-space (no horizontal)
        
        #hbox1_start
        #-------------------------------------------
        #containers-separators.
        hbox1 = gtk.HBox(False, 10) #file field and button examine.
        #gtk.HBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio horizontal entre hijos.
        
        #hbox1
        self.button1 = gtk.Button(_("Close"))
        self.button1.set_size_request(80, 35)
        self.button1.connect("clicked", self.on_close)
        hbox1.add(self.button1)
        
        halign1 = gtk.Alignment(1, 0, 0, 0) #horizontal container. right liagment.
        #xalign: espacio libre a la izquierda del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        #yalign: espacio libre vertical arriba del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        halign1.add(hbox1)
        
        vbox1.pack_start(halign1, False)
        #vbox.pack_start(child, expand=True, fill=True, padding=0)
        #-------------------------------------------
        #hbox1_end
        
        self.load_full_log()
        
        self.connect("response", self.on_close)
        self.vbox.pack_start(vbox1)
        self.show_all()
        self.run()

    def load_full_log(self):
        """"""
        try:
            with open(cons.LOG_FILE, "rb", cons.FILE_BUFSIZE) as fh:
                lines = fh.read()
        except EnvironmentError as err:
            lines = str(err)
            logger.warning("{0}".format(err))
        
        buffer = self.text_field.get_buffer()
        buffer.set_text(smartdecode(lines))

    def on_close(self, widget, other=None):
        """"""
        self.destroy() 
