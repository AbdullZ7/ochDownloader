import gtk
import gobject

import threading
import os #clase SaveFile
import sys
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons
import core.misc as misc
from core.api import api
from core.conf_parser import conf
from core.Container_Extractor import Container

import media_gui as media
from add_links_gui import AddLinks
from menu_gui import Menu
from popup_menu_button_gui import PopupMenuButton
from dialog_base import FileChooserDialog


class AddDownloads(gtk.VBox):
    """"""
    def __init__(self, list_gui, parent=None):
        gtk.VBox.__init__(self)
        
        self.__parent = parent
        self.list_gui = list_gui
        
        self.update_flag = False
        self.active_tab_flag = True
        
        #Estructura:
        #-------------------vbox1_start---------------
        #-------------------hbox4[halign1-left + halign4-right]-----------------------
        #-------------------vbox1_end----------------
        
        #detallado:
        #-------------------vbox1_start---------------
        #-------------------hbox4_start---------------
        #-------------------halign1_start-------------
        #-------------------hbox1-----------------------(save to field + examine button, left aligned)
        #-------------------halign1_end--------------
        #-------------------halign4_start------------(add links button, etc, right aligned)
        #-------------------halign2_start-------------
        #-------------------hbox2-----------------------
        #-------------------halign2_end--------------
        #-------------------halign4_end--------------
        #-------------------hbox4_end----------------
        #-------------------vbox1_end----------------
        
        #containers-separators.
        #self.vbox no puede ser cambiado en gtk.Dialog. Crear variable vbox y luego meterla en self.vbox.
        vbox1 = gtk.VBox(False, 5) #gtk.VBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio horizontal entre hijos.
        
        #vbox1_start
        #Check links field.
        #-------------------------------------------
        
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.store = gtk.ListStore(str, bool, str, str, str, str, str)#modelo de columnas. (4 columnas de strings y 1 booleana)
        
        #arma el cuadro con los items
        self.treeView = gtk.TreeView(self.store)
        self.treeView.set_rules_hint(True) #turna el color de los items, creo.
        scroll.add(self.treeView)
        
        #Columns item names.
        col_list = ["hidden_id_item", _("Add"), _("Status"), _("File Name"), _("Host"), _("Size"), _("Status Message")] #podria usar un frozenset, no se si lo soporta cython.
        self.create_columns(col_list)
        
        vbox1.pack_start(scroll)
        
        #Context Menu (pop-up)
        dl_selected_item = (gtk.MenuItem(), _("Download Selected"), self.on_accept)
        recheck_item = (gtk.MenuItem(), _("Re-check"), self.on_recheck)
        clear_item = (gtk.MenuItem(), _("Clear list"), self.on_clear_list)
        
        menu_items = (dl_selected_item, None, recheck_item, clear_item)
        self.ctx_menu = Menu(menu_items) #items selected
        self.treeView.connect("button-press-event", self.on_context_menu)
        
        #Select file field.
        #-------------------------------------------
        #containers-separators.
        hbox1 = gtk.HBox(False, 10) #file field and button examine.
        #gtk.HBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio horizontal entre hijos.
        hbox2 = gtk.HBox(False, 10) #buttons cancel and accept.
        
        #hbox1
        #label_save_to = gtk.Label("Save to:")
        #hbox1.add(label_save_to)
        self.paths_liststore = gtk.ListStore(str)
        cb_entry = gtk.ComboBoxEntry(self.paths_liststore)
        self.entry = cb_entry.child
        self.entry.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.entry.set_width_chars(35) #entry width
        
        self.paths_list = conf.get_save_dl_paths()
        self.load_save_paths()
        
        if not self.paths_list:
            default_path = cons.DLFOLDER_PATH
        else:
            default_path = self.paths_list[-1]
        
        #.decode(sys.getfilesystemencoding())
        self.entry.set_text(default_path.decode("utf-8")) #default entry path. Cuando cree el ejecutable, se puede crear una ruta al directorio asi: sys.path.append(path)
        hbox1.add(cb_entry)
        
        button = gtk.Button(_("..."))
        button.set_size_request(80, 35)
        button.connect("clicked", self.save_folder)
        hbox1.add(button)
        
        halign1 = gtk.Alignment(0, 0, 0, 0) #horizontal container. left liagment. #vertical container (estara vacio). gtk.Alignment(xalign=0.0, yalign=0.0, xscale=0.0, yscale=0.0)
        #xalign: espacio libre a la izquierda del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        #yalign: espacio libre vertical arriba del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        halign1.add(hbox1)
        
        down_arrow_image = media.get_image(media.DOWN, media.MEDIUM)
        download_selected_button = gtk.Button()
        download_selected_button.add(down_arrow_image)
        #self.button2.set_size_request(180, 35)
        download_selected_button.connect("clicked", self.on_accept)
        
        add_image = media.get_image(media.ADD, media.MEDIUM)
        add_button = gtk.Button()
        add_button.add(add_image)
        #button.set_size_request(80, 35)
        add_button.connect("clicked", self.on_add_links)
        
        
        icon_down = media.get_image(media.ARROW_DOWN, media.SMALL)
        #icon_down = gtk.image_new_from_file(os.path.join(cons.APP_PATH, "media", "arrow_down9.png"))
        #drop_down_image = gtk.image_new_from_stock(gtk.STOCK_GO_DOWN, gtk.ICON_SIZE_BUTTON)
        drop_down_button = PopupMenuButton(image=icon_down) #gtk.Button()
        drop_down_button.set_size_request(20, 35)
        
        import_item = (gtk.MenuItem(), _("Import Container"), self.on_import_container)
        recheck_item = (gtk.MenuItem(), _("Re-check"), self.on_recheck)
        clear_item = (gtk.MenuItem(), _("Clear list"), self.on_clear_list)
        
        menu_items = (import_item, None, recheck_item, clear_item)
        menu = Menu(menu_items) #items selected
        drop_down_button.set_menu(menu)
        
        #button5 = gtk.Button(_("Re-check"))
        #button5.set_size_request(80, 35)
        #button5.connect("clicked", self.on_recheck)
        
        halign4 = gtk.Alignment(1, 0, 0, 0) #horizontal container. right liagment.
        hbox2.add(download_selected_button)
        hbox2.add(add_button)
        hbox2.add(drop_down_button)
        halign4.add(hbox2)
        
        hbox4 = gtk.HBox(False, 0) #two aligment widgets
        hbox4.add(halign1)
        hbox4.add(halign4)
        
        vbox1.pack_start(hbox4, False, False) #pack_start(child, expand=True, fill=True, padding=0)
        
        #-------------------------------------------
        #vbox1_end
        
        #entry.get_text()
        #checking thread stuff.
        self.cancelled = False #si se cancelo el checkeo, terminar thread.
        #self.th = threading.Thread(group=None, target=self.checking_links, name=None).start() #ckeck links.
        
        self.pack_start(vbox1)

    def create_columns(self, col_list):
        """"""
        for item in col_list:
            id_col = col_list.index(item)
            if item != _("Add"):
                rendererText = gtk.CellRendererText() #pide el primer item que ira en la columna (text=0) o segundo, etc...
                rendererText.set_property("ellipsize", 3) #2= middle, 3 = right, 1 = left
                column = gtk.TreeViewColumn(item, rendererText, text=id_col)
                column.set_sort_column_id(id_col) #ordenar columna
                column.set_resizable(True)
                column.set_expand(True)
                column.set_min_width(1)
                if item == "hidden_id_item": #no mostrar columna de id_item
                    column.set_visible(False)
                elif item == _("File Name"):
                    rendererText.set_property("ellipsize", 2)
            else: #selection box column.
                rendererToggle = gtk.CellRendererToggle()
                #rendererToggle.set_property('activatable', True)
                column = gtk.TreeViewColumn(None, rendererToggle) #name = None
                column.add_attribute(rendererToggle, 'active', id_col)
                column.set_min_width(21)
                rendererToggle.connect("toggled", self.on_toggled, id_col)
            self.treeView.append_column(column)
    
    def load_save_paths(self):
        """"""
        for path in self.paths_list:
            self.paths_liststore.prepend([path])
    
    def on_context_menu(self, widget, event):
        """"""
        if event.button == 3:
            #model, rows = self.treeView.get_selection().get_selected_rows()
            #if rows:
            self.ctx_menu.popup(None, None, None, event.button, event.time)
    
    def on_toggled(self, celltoggled, path, id_col): #id_col = numero de columna, path= numero de fila
        """"""
        model = self.treeView.get_model()
        if celltoggled.get_active(): #devuelve True, si el check estaba activado, sino false.
            model[path][id_col] = False
        else:
            model[path][id_col] = True
    
    def on_recheck(self, widget):
        """
        Recheck only non alive items.
        """
        api.recheck_items()
    
    def on_clear_list(self, widget):
        """"""
        self.store.clear() #clear all rows in the liststore
        api.clear_pending()
    
    def on_import_container(self, widget=None): #import_links (importar contenedor)
        """"""
        
        openfile = FileChooserDialog(title=_("Open File"), parent=self.__parent, action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        openfile.set_default_response(gtk.RESPONSE_OK)
        
        filter = gtk.FileFilter()
        filter.set_name("OCH Files")
        filter.add_pattern("*.och")
        openfile.add_filter(filter)
        
        response = openfile.run()
        if response == gtk.RESPONSE_OK:
            #.decode(sys.getfilesystemencoding())
            fileh = openfile.get_filename().decode("utf-8") if response == gtk.RESPONSE_OK else None #ruta + nombre de archivo seleccionado
            logger.info("File opened: {0}".format(openfile.get_filename().decode(sys.getfilesystemencoding())))

            if fileh:
                container = Container(fileh)
                container.extract_links()
                links_list = container.get_linklist()
                
                if links_list:
                    self.checking_links(links_list, copy_link=False)
                
                #SaveFiles(linklist, self.download_manager, self.list_gui) #instancia de clase. SaveFiles(lista, clase, clase)
        openfile.destroy()
    
    def on_add_links(self, widget):
        """
        DONE: luego de aniadir links, se deberia poder seguir aniadiendo. Y limpiar aniadidos
        """
        add_links_dlg = AddLinks(parent=self.__parent)
        links_list = add_links_dlg.links_list
        if links_list: #se agregaron items.
            self.checking_links(links_list)

    def checking_links(self, links_list, copy_link=True):
        """
        Agregar items a las columnas
        DONE: Agrergar posibilidad de recherckear items que no estan vivos.
        DONE: detener el update de la lista (desde el main_gui), cuando se cambia a otra pestania (senial switch-notebook)
        TODO: Agregar columna que muestre la url del enlace, none para los agregados desde un .och
        """
        for link in links_list:
            download_item = api.create_download_item(cons.UNKNOWN, 0, link, copy_link) #return download_item object
            self.store.append([download_item.id, True, cons.LINK_CHECKING, cons.UNKNOWN, None, None, None])
            #checking start.
            #threading.Thread(group=None, target=self.download_manager.plugin_link_checking, name=None, args=(download_item, )).start()
        api.start_checking()
        
        self.start_update()
    
    def start_update(self):
        """"""
        if not self.update_flag:
            self.update_flag = True
            gobject.timeout_add(1000, self.update_checking_status)

    def update_checking_status(self): #this method steals cycles, its not a new thread
        """"""
        #self.download_manager.clear_pending() #Erase pending_downloads list.
        items_list = api.get_checking_update()
        for download_item in items_list:
            #link_status, file_name, host, size = self.download_manager.plugin_link_checking(download_item)
            for row in self.store:
                if row[0] == download_item.id:
                    row[2] = download_item.link_status
                    row[3] = download_item.name
                    row[4] = download_item.host
                    row[5] = misc.size_format(download_item.size)
                    row[6] = download_item.link_status_msg
            #if not self.download_manager.pending_downloads:
                #return False
        return True #keep it updating,

    def save_folder(self, widget):
        """
        Cuadro de dialogo para elegir donde se quiere guardar lo descargado.
        """
        openfolder = FileChooserDialog(title=_("Open Folder"), parent=self.__parent, action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
        openfolder.set_default_response(gtk.RESPONSE_OK)
        
        response = openfolder.run()
        
        if response == gtk.RESPONSE_OK:
            self.entry.set_text(openfolder.get_filename().decode("utf-8")) #.decode(sys.getfilesystemencoding())) #("utf-8"))
            
        openfolder.destroy()

    def on_accept(self, widget):
        """"""
        save_to_path = self.entry.get_text().decode("utf-8") #(sys.getfilesystemencoding())
        try:
            self.paths_list.remove(save_to_path)
        except ValueError:
            if len(self.paths_list) > 5:
                self.paths_list.pop(0)
        self.paths_list.append(save_to_path)
        self.paths_liststore.clear()
        self.load_save_paths()
        conf.set_save_dl_paths(self.paths_list)
        
        #remover items no seleccionados de pending_downloads.
        model = self.treeView.get_model()
        id_add_list = []
        iters = []
        for row in model: #desactivar los otros antes de activar este.
            if row[1] and row[2] != cons.LINK_DEAD and row[4] != cons.UNSUPPORTED: #id_col = 1, toggle. True (active) or False
                id_add_list.append(row[0])
                iters.append(row.iter) #row.iter returns a treeiter
        [model.remove(iter) for iter in iters]
        
        item_list = api.get_added_items(id_add_list)
        
        api.downloader_init(item_list, save_to_path) #iniciar threads de descarga.
        self.list_gui.store_items(item_list) #agregar links a la lista GUI