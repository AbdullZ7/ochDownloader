import gtk
import gobject

import threading
import os #clase SaveFile

import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons

class SaveFiles(gtk.Dialog):
    """
    DEPRECATED
    """
    def __init__(self, linklist, download_manager, list_gui):
        """"""
        gtk.Dialog.__init__(self)
        self.set_title(_("Select Folder"))
        self.set_size_request(500, 330)
        
        self.linklist = linklist #link_list
        self.download_manager = download_manager #clase DownloadManager del download_manager
        self.list_gui = list_gui #clase List
        
        #Estructura:
        #-------------------vbox1_start---------------
        #-------------------frame------------------------
        #-------------------hbox1-----------------------
        #-------------------hbox2-----------------------
        #-------------------vbox1_end----------------
        
        #containers-separators.
        #self.vbox no puede ser cambiado en gtk.Dialog. Crear variable vbox y luego meterla en self.vbox.
        vbox1 = gtk.VBox(False, 5) #gtk.VBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio horizontal entre hijos.
        
        #vbox1_start
        #Check links field.
        #-------------------------------------------
        #frame
        frame = gtk.Frame(_("Link checker:"))
        #frame.set_border_width(10)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        frame.add(scroll)
        
        self.store = gtk.ListStore(str, bool, str, str, str, str)#modelo de columnas. (4 columnas de strings y 1 booleana)
        
        #arma el cuadro con los items
        self.treeView = gtk.TreeView(self.store)
        self.treeView.set_rules_hint(True) #turna el color de los items, creo.
        scroll.add(self.treeView)
        
        #Columns item names.
        col_list = ["hidden_id_item", _("Add"), _("Status"), _("Name"), _("Host"), _("Size")] #podria usar un frozenset, no se si lo soporta cython.
        self.create_columns(col_list)
        
        vbox1.pack_start(frame)
        
        #Select file field.
        #-------------------------------------------
        #containers-separators.
        hbox1 = gtk.HBox(False, 10) #file field and button examine.
        #gtk.HBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio horizontal entre hijos.
        hbox2 = gtk.HBox(False, 10) #buttons cancel and accept.
        
        #hbox1
        self.entry = gtk.Entry()
        self.entry.set_text(cons.DLFOLDER_PATH) #default entry path. Cuando cree el ejecutable, se puede crear una ruta al directorio asi: sys.path.append(path)
        self.entry.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.entry.set_width_chars(40) #entry width
        hbox1.add(self.entry)
        
        button = gtk.Button(_("Examine..."))
        button.set_size_request(80, 35)
        button.connect("clicked", self.save_folder)
        hbox1.add(button)
        
        halign1 = gtk.Alignment(1, 0, 0, 0) #horizontal container. right liagment. #vertical container (estara vacio). gtk.Alignment(xalign=0.0, yalign=0.0, xscale=0.0, yscale=0.0)
        #xalign: espacio libre a la izquierda del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        #yalign: espacio libre vertical arriba del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        halign1.add(hbox1)
        
        vbox1.pack_start(halign1, False, False) #pack_start(child, expand=True, fill=True, padding=0)
        
        #hbox2
        button = gtk.Button(_("Cancel"))
        button.set_size_request(80, 35)
        button.connect("clicked", self.on_close)
        hbox2.add(button)
        
        self.button2 = gtk.Button(_("Accept"))
        self.button2.set_size_request(80, 35)
        self.button2.set_sensitive(False) #temporal
        self.button2.connect("clicked", self.on_accept)
        hbox2.add(self.button2)
        
        halign2 = gtk.Alignment(1, 0, 0, 0) #horizontal container. right liagment.
        halign2.add(hbox2)
        
        vbox1.pack_start(halign2, False, False)
        #-------------------------------------------
        #vbox1_end
        
        #entry.get_text()
        #checking thread stuff.
        self.cancelled = False #si se cancelo el checkeo, terminar thread.
        gobject.idle_add(self.checking_links)
        #self.th = threading.Thread(group=None, target=self.checking_links, name=None).start() #ckeck links.
        
        self.connect("response", self.on_close)
        self.vbox.pack_start(vbox1)
        self.show_all()
        self.run()

    def create_columns(self, col_list):
        """
        TODO: Es practicamente la misma funcion que en list_gui. Puede que sea mejor crear un modulo acumulando funciones similares del gui.
        Crea las columnas de la lista
        """
        for item in col_list:
            id_col = col_list.index(item)
            if item != _("Add"):
                rendererText = gtk.CellRendererText() #pide el primer item que ira en la columna (text=0) o segundo, etc...
                column = gtk.TreeViewColumn(item, rendererText, text=id_col)
                column.set_sort_column_id(id_col) #ordenar columna
                if item == "hidden_id_item": #no mostrar columna de id_item
                        column.set_visible(False)
            else: #selection box column.
                rendererToggle = gtk.CellRendererToggle()
                #rendererToggle.set_property('activatable', True)
                column = gtk.TreeViewColumn(item, rendererToggle)
                column.add_attribute(rendererToggle, 'active', id_col)
                rendererToggle.connect("toggled", self.on_toggled, id_col)
            self.treeView.append_column(column)
    
    def on_toggled(self, celltoggled, path, id_col): #id_col = numero de columna, path= numero de fila
        """"""
        model = self.treeView.get_model()
        if celltoggled.get_active(): #devuelve True, si el check estaba activado, sino false.
            model[path][id_col] = False
        else:
            model[path][id_col] = True
    
    def item_selection(self):
        """
        TODO: aniadir cuadro de seleccion a las filas, agregar a la descarga solo los archivos que coinciden con los item_id seleccionados.
        """
        pass

    def checking_links(self):
        """
        NUevo thread. testear en windows.
        Agregar items a las columnas
        TODO: En lugar de mandar la lista de links, mandar link por link y agregar link por link al gui.
        Mostrar status 'checking' por cada link, luego rellenar las filas con los datos
        TODO: Agrergar posibilidad de recherckear items que no estan vivos.
        """
        self.th = threading.Thread(group=None, target=self.thread_checking, name=None).start()

    def thread_checking(self):
        """"""
        self.download_manager.clear_pending() #Erase pending_downloads list.
        for link in self.linklist:
            self.store.append([None, True, _("Checking"), cons.UNKNOWN, None, None])
        for link, row in zip(self.linklist, self.store): #recorrer las listas al mismo tiempo, ya que tienen la misma cantidad de items.
            id_item, link_status, file_name, host, size = self.download_manager.plugin_check(link)
            row[0], row[2], row[3], row[4], row[5] = id_item, link_status, file_name, host, size
            if self.cancelled:
                break
        self.button2.set_sensitive(True)

    def save_folder(self, widget):
        """
        Cuadro de dialogo para elegir donde se quiere guardar lo descargado.
        """
        openfolder = gtk.FileChooserDialog(title=_("Open Folder"), action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        openfolder.set_default_response(gtk.RESPONSE_OK)
        
        response = openfolder.run()
        
        if response == gtk.RESPONSE_OK:
            self.entry.set_text(openfolder.get_filename().decode("utf-8"))
            
        openfolder.destroy()

    def on_accept(self, widget):
        """"""
        save_to_path = self.entry.get_text().decode("utf-8")
        
        #remover items no seleccionados de pending_downloads.
        model = self.treeView.get_model()
        for row in model: #desactivar los otros antes de activar este.
            if not row[1]: #id_col = 1, toggle. True (active) or False
                self.download_manager.remove_pending_item(row[0]) #id_col = 0, id_item.
        
        self.download_manager.downloader_init(save_to_path) #iniciar threads de descarga.
        self.list_gui.store_items() #agregar links a la lista GUI
        
        self.destroy() 

    def on_close(self, widget, other=None):
        """"""
        self.cancelled = True
        self.destroy() 
        
