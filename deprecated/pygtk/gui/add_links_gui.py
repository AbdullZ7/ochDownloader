import gtk
import gobject

import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
from core.misc import links_parser

from dialog_base import Dialog


class AddLinks(Dialog):
    """"""
    def __init__(self, parent=None):
        """"""
        Dialog.__init__(self)
        self.set_title(_("Select Folder"))
        self.set_size_request(500, 330)
        self.set_transient_for(parent)

        self.links_list = [] #empty list.
        
        #containers-separators.
        #self.vbox no puede ser cambiado en gtk.Dialog. Crear variable vbox y luego meterla en self.vbox.
        vbox1 = gtk.VBox(False, 20) #gtk.VBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio vertical entre hijos.
        vbox1.set_border_width(10) #outside-space
        
        #vbox1_start
        #Servers dropdown menu (ComboBox).
        #-------------------------------------------
        #frame1
        frame = gtk.Frame(_("Paste Your Links (one link per line):"))
        
        self.paste_field = gtk.TextView()
        self.paste_field.set_editable(True)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_border_width(10)
        
        #arma el cuadro con los items
        scroll.add(self.paste_field)
        
        frame.add(scroll)
        vbox1.pack_start(frame)
        #vbox.pack_start(child, expand=True, fill=True, padding=0) #padding = vertical-space (no horizontal)
        
        #hbox1_start
        #-------------------------------------------
        #containers-separators.
        hbox1 = gtk.HBox(False, 10) #file field and button examine.
        #gtk.HBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio horizontal entre hijos.
        
        #hbox1
        self.button1 = gtk.Button(None, gtk.STOCK_CANCEL)
        self.button1.set_size_request(80, 35)
        self.button1.connect("clicked", self.on_close)
        hbox1.add(self.button1)
        
        self.button2 = gtk.Button(None, gtk.STOCK_OK)
        self.button2.set_size_request(80, 35)
        self.button2.connect("clicked", self.on_add)
        hbox1.add(self.button2)
        
        halign1 = gtk.Alignment(1, 0, 0, 0) #horizontal container. right liagment.
        #xalign: espacio libre a la izquierda del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        #yalign: espacio libre vertical arriba del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        halign1.add(hbox1)
        
        vbox1.pack_start(halign1, False)
        #vbox.pack_start(child, expand=True, fill=True, padding=0)
        #-------------------------------------------
        #hbox1_end
        
        self.connect("response", self.on_close)
        self.vbox.pack_start(vbox1)
        self.show_all()
        self.run()
    
    def on_add(self, widget, other=None):
        """"""
        
        buffer = self.paste_field.get_buffer()
        start, end = buffer.get_bounds()
        text_pasted = buffer.get_text(start, end)
            
        tmp_list = links_parser(text_pasted) #funcion importada de misc.py
        
        for link in tmp_list: #very lame
            self.links_list.append(link)
        
        self.destroy()
    
    def on_close(self, widget, other=None):
        """"""
        self.destroy() 
    
