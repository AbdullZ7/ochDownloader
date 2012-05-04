import gtk
import gobject

import threading
import os
import sys
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
import core.cons as cons
import core.misc as misc
from core.api import api
from core.config import config_parser
from core.events import events

#Gui
import media_gui as media
from dlg_gui import DlgGui #Dialog
from tree_view_gui import DnDTreeView #dragndrop_tree_view
from menu_gui import Menu

#constants
WIDGET, TITLE, CALLBACK = range(3)


class List(gtk.VBox): #DownloadsList
    """
    Lista de archivos descargando.
    """
    def __init__(self, parent=None):
        """"""
        gtk.VBox.__init__(self)
        
        self.__parent = parent

        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.store = self.create_model() #crear columnas y
        self.update_flag = False #flag para que el update de la lista se haga solo si ya no esta corriendo. False = detenido. True = Corriendo.
        self.active_tab_flag = True
        #self.rows_buffer = {} #{id_item: row_obj, }
        
        #arma el cuadro con los items
        self.treeView = DnDTreeView(self.store)
        self.treeView.set_rules_hint(True) #turna el color de los items, creo.
        #self.treeView.set_reorderable(True) #change order by drag'n'drop.
        scroll.add(self.treeView)
        
        self.rows_buffer = self.treeView.rows_buffer #{id_item: row_obj, }
        
        #self.treeView.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        #Columns item names. Host = 3 columns in 1
        col_list = ["hidden_id_item", _("Status"), _("File Name"), _("Host"), _("Size"), _("Complete"), _("Progress"), _("Time"), _("Remain"), _("Speed"), _("Status Message")] #podria usar un frozenset, no se si lo soporta cython.
        self.create_columns(col_list)
        
        #status icons
        self.icons_dict = self.get_icons() #return dict {cons.status_running: icon, }
        
        #self.treeView.add_events(gtk.gdk.KEY_PRESS)
        self.treeView.connect("key_press_event", self.keyboard_event)
        
        #Context Menu (pop-up)
        open_folder_item = (gtk.MenuItem(), _("Open destination folder"), self.on_open_folder)
        copy_link_item = (gtk.MenuItem(), _("Copy link"), self.on_copy_link)
        password_item = (gtk.MenuItem(), _("Add password"), self.on_password)
        delete_item = (gtk.MenuItem(), _("Delete"), self.on_delete)
        
        clear_completed_item = (gtk.MenuItem(), _("Clear Completed"), self.on_clear_completed)
        start_all_item = (gtk.MenuItem(), _("Start all"), self.on_start_all)
        stop_all_item = (gtk.MenuItem(), _("Stop all"), self.on_stop_all)
        
        self.menu_items = (open_folder_item, copy_link_item, password_item, delete_item)
        menu_generic_items = (None, start_all_item, stop_all_item, clear_completed_item)
        self.ctx_menu = Menu(self.menu_items+menu_generic_items) #items selected
        self.treeView.connect("button-press-event", self.on_context_menu)

        self.pack_start(scroll)
 
    def keyboard_event(self, widget, event):
        """"""
        if gtk.gdk.keyval_name(event.keyval) == "Delete": #supr. key
            self.on_delete()
    
    def on_context_menu(self, widget, event):
        """
        TODO: Mandar todo lo q tiene q ver con context_menu a otro modulo.
        """
        if event.button == 3: #right click
            selection = self.treeView.get_selection()
            model, rows = selection.get_selected_rows()
            if not rows or len(rows) == 1:
                try:
                    path, col, cellx, celly = self.treeView.get_path_at_pos(int(event.x), int(event.y))
                except TypeError: #none selected.
                        is_sensitive = False
                        selection.unselect_all()
                else: #one selected.
                    is_sensitive = True
                    self.treeView.grab_focus()
                    selection.select_path(path)
            else:
                is_sensitive = True
            
            [item[WIDGET].set_sensitive(is_sensitive) for item in self.menu_items]
            self.ctx_menu.popup(None, None, None, event.button, event.time)
            
            if len(rows) > 1: #stop signal (so the rows remain selected)
                return True

    def on_open_folder(self, widget):
        """"""
        model, rows = self.treeView.get_selection().get_selected_rows()
        if rows:
            paths_list = []
            items_list = api.get_download_items([model[row][0] for row in rows])
            for download_item in items_list:
                folder_path = download_item.path
                if folder_path not in paths_list:
                    #misc.open_folder_window(folder_path)
                    threading.Thread(group=None, target=misc.open_folder_window, name=None, args=(folder_path, )).start()
                    paths_list.append(folder_path)
    
    def on_copy_link(self, widget):
        """"""
        model, rows = self.treeView.get_selection().get_selected_rows()
        if rows:
            items_list = api.get_download_items([model[row][0] for row in rows])
            links_list = [download_item.link for download_item in items_list if download_item.can_copy_link]
            clipboard = gtk.Clipboard()
            clipboard.set_text('\n'.join(links_list))
    
    def on_password(self, widget):
        """"""
        model, rows = self.treeView.get_selection().get_selected_rows()
        if rows:
            entry = gtk.Entry()
            entry.add_events(gtk.gdk.KEY_RELEASE_MASK)
            entry.set_width_chars(25) #entry width
            
            m = DlgGui(self.__parent, None, _("Password"), None, True, append_widget=entry)
            
            pwd = entry.get_text().strip()
            
            if m.accepted and pwd:
                events.trigger_pwd(pwd)
    
    def on_delete(self, widget=None):
        """"""
        model, rows = self.treeView.get_selection().get_selected_rows()
        if rows:
            message = _("Do you want to remove this download? (downloaded segments will be deleted)")
            m = DlgGui(self.__parent, gtk.STOCK_DIALOG_WARNING, _("Remove Files"), message, True, True)
            if m.accepted:
                id_items_list = []
                iters = []
                for row in rows:
                    iters.append(model[row].iter)
                    id_item = model[row][0]
                    id_items_list.append(id_item)
                    del self.rows_buffer[id_item]
                #id_items_list = [model[row][0] for row in rows]
                [model.remove(iter) for iter in iters]
                api.delete_download(id_items_list)
    
    def on_start_all(self, widget):
        """
        BUG: El boton start y stop no cambia.
        """
        iditem_list = self.treeView.get_id_item_list()
        api.start_all(iditem_list)
        stopped_icon = self.icons_dict[cons.STATUS_STOPPED]
        queue_icon = self.icons_dict[cons.STATUS_QUEUE]
        for row in self.rows_buffer.values():
            if row[1] == stopped_icon:
                row[1] = queue_icon
        self.get_status() #iniciar update de lista.
    
    def on_stop_all(self, widget=None):
        """
        BUG: El boton start y stop no cambia.
        """
        api.stop_all()
        stopped_icon = self.icons_dict[cons.STATUS_STOPPED]
        queue_icon = self.icons_dict[cons.STATUS_QUEUE]
        for row in self.rows_buffer.values():
            if row[1] == queue_icon:
                row[1] = stopped_icon
    
    def on_clear_completed(self, widget):
        """"""
        model = self.treeView.get_model()
        finished_icon = self.icons_dict[cons.STATUS_FINISHED]
        iters = []
        for row in self.rows_buffer.values():
            if row[1] == finished_icon:
                iters.append(row.iter)
                del self.rows_buffer[row[0]]
                #todo: remove from complete_downloads
        [model.remove(iter) for iter in iters]

    def get_status(self):
        """
        DONE: Se llama a self.update_status cada vez q se agrega un archivo (incluso si ya esta corriendo). Hacer que no se llame si ya esta corriendo.
        DONE: Mejorar este metodo + downloadmanager.get_thread + downloadmanager.thread_manager.get_status.
        Gobject roba ciclos, no es un thread aparte (en teoria)
        """
        if not self.update_flag: #si el flag = True, el update ya esta corriendo. Si es False entramos.
            self.update_flag = True
            gobject.timeout_add(1000, self.update_status) #auto actualizar status cada 1 seg.
            logger.debug("list_update = True")
    
    def update_status(self):
        """"""
        downloads_list = api.get_status()
        for download_item in downloads_list:
            try:
                row = self.rows_buffer[download_item.id]
                #row[0] = download_item.id #this column is hidden and wont be modificated.
                row[1] = self.icons_dict[download_item.status] #col 1
                row[2] = download_item.name #col 2
                #row[3] = download_item.host #download_item.host #col 3
                row[4] = self.icons_dict[cons.DL_RESUME] if download_item.can_resume else None #download_item.host #col 3
                row[5] = self.icons_dict[cons.DL_PREMIUM] if download_item.is_premium else None #download_item.host #col 3
                row[6] = misc.size_format(download_item.size) if download_item.size else None
                row[7] = misc.size_format(download_item.size_complete) if download_item.size_complete else None
                row[8] = download_item.progress
                row[9] = misc.time_format(download_item.time) if download_item.time else None
                row[10] = misc.time_format(download_item.time_remain) if download_item.time_remain else None
                row[11] = misc.speed_format(download_item.speed) if download_item.speed else None
                row[12] = download_item.status_msg if not download_item.fail_count else "{0} ({1} #{2})".format(download_item.status_msg,_("Retry"), download_item.fail_count)
            except KeyError as err:
                logger.debug(err)
        #if not self.download_manager.active_downloads + self.download_manager.queue_downloads + self.download_manager.stopped_downloads: #si ya no hay mas descargas activas o en cola detener este loop.
            #logger.debug("list_update = False")
            #self.update_flag = False #cuando update_flag = False, sabemos que ya no esta corriendo...
            #return False
        
        return True #hace que se actualicen los valores mas de una vez (hasta el final).

    def create_model(self):
        """
        Crear columnas
        """
        store = gtk.ListStore(str, gtk.gdk.Pixbuf, str, gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, str, str, int, str, str, str, str) #tipo de item de cada columana (nombre de link, host, tamanio, porcentaje, vel.)
        
        return store

    def store_items(self, item_list):
        """
        Agregar nuevos items a las columnas
        """
        #self.dnd_flag = False #no afectar metodo dragndrop
        for download_item in item_list: #in self.download_manager.pending_downloads:
            self.get_status() #iniciar update_list del gui
            
            size_file = misc.size_format(download_item.size) if download_item.size else None
            size_complete = misc.size_format(download_item.size_complete) if download_item.size_complete else None
            time = misc.time_format(download_item.time) if download_item.time else None
            host_icon = self.get_host_icon(download_item.host)
            
            self.store.append([download_item.id, self.icons_dict[download_item.status], download_item.name, host_icon, None, None, size_file, size_complete, download_item.progress, time, None, None, download_item.status_msg]) #store.append([act[0], act[1], act[2]], ) futura lista con tamanio de archivo, icono, etc
            
            self.rows_buffer[download_item.id] = self.store[-1] #row just added
            
        
        #self.dnd_flag = True #volver a habilitar el metodo dragndrop

    def create_columns(self, col_list):
        """
        Crea las columnas de la lista
        TODO: Guardar el tamanio de la columna nombre en el config.ini al resizear.
        """
        id_col = 0
        for item in col_list:
            #id_col = col_list.index(item)
            if item not in(_("Status"), _("Progress"), _("Host")): #si no es la barra de progreso ni el estado
                rendererText = gtk.CellRendererText() #pide el primer item que ira en la columna (text=0) o segundo, etc...
                rendererText.set_property("ellipsize", 3) #2= middle, 3 = right, 1 = left
                column = gtk.TreeViewColumn(item, rendererText, text=id_col)
                column.set_resizable(True)
                column.set_expand(True)
                column.set_min_width(1)
                if item == "hidden_id_item": #no mostrar columna de id_item
                    column.set_visible(False)
                    column.set_resizable(False)
                elif item == _("File Name"):
                    rendererText.set_property("ellipsize", 2)
                    rendererText.set_fixed_size(150, -1)
                #elif item == _("Status Message"):
                    #column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
                    #column.set_min_width(110) #dont let expand like crazy...
            elif item == _("Status"):
                renderPixbuf = gtk.CellRendererPixbuf()
                column = gtk.TreeViewColumn(None, renderPixbuf) #name = None
                column.add_attribute(renderPixbuf, 'pixbuf', id_col)
                column.set_expand(False)
                column.set_min_width(21)
            elif item == _("Host"):
                renderPixbuf = gtk.CellRendererPixbuf()
                renderPixbuf_2 = gtk.CellRendererPixbuf()
                renderPixbuf_3 = gtk.CellRendererPixbuf()
                column = gtk.TreeViewColumn(item) #name = None
                column.pack_start(renderPixbuf, False)
                column.pack_start(renderPixbuf_2, False)
                column.pack_start(renderPixbuf_3, False)
                column.add_attribute(renderPixbuf, 'pixbuf', id_col)
                id_col += 1
                column.add_attribute(renderPixbuf_2, 'pixbuf', id_col)
                id_col += 1
                column.add_attribute(renderPixbuf_3, 'pixbuf', id_col)
                column.set_expand(True)
                column.set_min_width(1)
            else: #barra de progreso.
                rendererProgress = gtk.CellRendererProgress()
                column = gtk.TreeViewColumn(item, rendererProgress)
                column.add_attribute(rendererProgress, 'value', id_col) #aniadir variable a la barra.
                column.set_expand(True)
                column.set_min_width(1)
            #column.set_sort_column_id(id_col) #ordenar columna
            #column.set_spacing(25)
            self.treeView.append_column(column)
            id_col += 1

    def get_host_icon(self, host):
        """"""
        try:
            return self.icons_dict[host]
        except KeyError:
            try:
                self.icons_dict[host] = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(cons.PLUGINS_PATH, host, "favicon.ico").decode(sys.getfilesystemencoding()), 16, 16)
            except Exception as err:
                logger.warning(err)
                self.icons_dict[host] = None
        return self.icons_dict[host]

    def get_icons(self):
        """"""
        #running = self.treeView.render_icon(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_MENU)
        running = media.get_pixbuf(media.START, media.SMALL)
        stopped = media.get_pixbuf(media.STOP, media.SMALL)
        queue = media.get_pixbuf(media.QUEUE, media.SMALL)
        finished = media.get_pixbuf(media.CHECK, media.SMALL)
        error = media.get_pixbuf(media.X_MARK, media.SMALL)
        
        resume = media.get_pixbuf(media.REFRESH, media.SMALL)
        premium = media.get_pixbuf(media.ACCOUNTS, media.SMALL)
        
        return {cons.STATUS_RUNNING: running, cons.STATUS_STOPPED: stopped,
                cons.STATUS_QUEUE: queue, cons.STATUS_FINISHED: finished,
                cons.STATUS_ERROR: error, 
                cons.DL_RESUME: resume, cons.DL_PREMIUM: premium}

    