import datetime
import threading
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import pygtk
import gtk
import gobject

import core.misc as misc

#from gui.dialog_base import Dialog
from gui.menu_gui import Menu

#constants
WIDGET, TITLE, CALLBACK = range(3)


class HistoryContainer(gtk.VBox):
    """"""
    def __init__(self, history_cls, parent):
        """"""
        gtk.VBox.__init__(self)
        self.history_cls = history_cls
        #self.__parent = parent
        
        self.history_tab = None
    
    def on_load(self):
        """"""
        self.history_tab = HistoryTab(self.history_cls)
        self.pack_start(self.history_tab)
        logger.debug("History Container loaded")
    
    def on_close(self):
        if self.history_tab:
            self.history_tab.on_close()
            logger.debug("History Container closed")


class HistoryTab(gtk.VBox):
    """"""
    def __init__(self, history_cls):
        """"""
        gtk.VBox.__init__(self)
        #Dialog.__init__(self)
        #self.set_transient_for(parent)
        #self.set_title("History")
        #self.set_size_request(550, 260)
        
        #self.__parent = parent
        self.history_cls = history_cls
        
        self.limit = 50
        self.offset = 0
        
        hbox = gtk.HBox(False, 10)
        self.search_entry = gtk.Entry()
        self.search_entry.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.search_entry.set_width_chars(25) #entry width
        #self.search_entry.set_size_request(-1, 35)
        self.search_entry.set_inner_border(gtk.Border(3, 3, 6, 6))
        self.search_entry.set_activates_default(True)
        self.search_entry.connect("activate", self.on_search)
        hbox.pack_start(self.search_entry, False, False)
        button = gtk.Button(_("Search"))
        button.set_size_request(80, 35)
        button.connect("clicked", self.on_search)
        hbox.pack_start(button, False, False)
        
        #self.vbox.pack_start(hbox, False, False)
        self.pack_start(hbox, False, False)
        
        
        self.button_pre = gtk.Button(_("Previous"))
        self.button_pre.set_size_request(-1, 25)
        self.button_pre.connect("clicked", self.on_previous)
        #self.vbox.pack_start(self.button_pre, False)
        self.pack_start(self.button_pre, False)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.store = gtk.ListStore(str, str, str, str, str, str)#modelo de columnas. (4 columnas de strings y 1 booleana)
        
        #arma el cuadro con los items
        self.treeView = gtk.TreeView(self.store)
        self.treeView.set_rules_hint(True) #turna el color de los items, creo.
        self.treeView.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        scroll.add(self.treeView)
        
        #Columns item names.
        col_list = [_("File Name"), _("Size"), _("Complete"), _("Date Time"), _("Link"), _("Directory")] #podria usar un frozenset, no se si lo soporta cython.
        self.create_columns(col_list)
        
        #self.vbox.pack_start(scroll)
        self.pack_start(scroll)
        
        self.button_next = gtk.Button(_("Next"))
        self.button_next.set_size_request(-1, 25)
        self.button_next.connect("clicked", self.on_load_items)
        #self.vbox.pack_start(self.button_next, False)
        self.pack_start(self.button_next, False)
        
        
        #Context Menu (pop-up)
        open_folder_item = (gtk.MenuItem(), _("Open destination folder"), self.on_open_folder)
        copy_link_item = (gtk.MenuItem(), _("Copy link"), self.on_copy_link)
        
        self.menu_items = (open_folder_item, copy_link_item)
        self.ctx_menu = Menu(self.menu_items) #items selected
        self.treeView.connect("button-press-event", self.on_context_menu)
        
        
        self.on_load_items()
        
        #self.connect("response", self.on_close)
        
        self.show_all()
        #self.run()
    
    def on_context_menu(self, widget, event):
        """
        taken from list_gui
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
            #items_list = self.download_manager.get_download_items([model[row][0] for row in rows])
            
            for row in rows:
                folder_path = model[row][-1]
                if folder_path not in paths_list:
                    threading.Thread(group=None, target=misc.open_folder_window, name=None, args=(folder_path, )).start()
                    paths_list.append(folder_path)
    
    def on_copy_link(self, widget):
        """"""
        model, rows = self.treeView.get_selection().get_selected_rows()
        if rows:
            links_list = [model[row][-2] for row in rows if model[row][-2] is not None]
            clipboard = gtk.Clipboard()
            clipboard.set_text('\n'.join(links_list))
    
    def create_columns(self, col_list):
        """"""
        for item in col_list:
            id_col = col_list.index(item)
            rendererText = gtk.CellRendererText() #pide el primer item que ira en la columna (text=0) o segundo, etc...
            rendererText.set_property("ellipsize", 3) #2= middle, 3 = right, 1 = left
            column = gtk.TreeViewColumn(item, rendererText, text=id_col)
            #column.set_sort_column_id(id_col) #ordenar columna
            column.set_resizable(True)
            column.set_expand(True)
            column.set_min_width(1)
            if item == _("File Name"):
                rendererText.set_property("ellipsize", 2)
            self.treeView.append_column(column)
    
    def on_search(self, widget):
        """"""
        self.offset = 0
        self.on_load_items()
    
    def on_previous(self, widget):
        """"""
        self.offset -= self.limit * 2
        self.on_load_items()
    
    def on_load_items(self, widget=None): #TEST when the items are 50, 51
        """"""
        self.validate_request()
        self.button_next.set_sensitive(True)
        self.button_pre.set_sensitive(True)
        match_term = self.search_entry.get_text()
        data_list = self.history_cls.get_data(self.offset, self.limit, match_term)
        self.store.clear()
        [self.store.append((name, misc.size_format(size), misc.size_format(complete), date_.strftime("%d-%m-%y %H:%M"), link, path))
            for id, name, link, size, complete, path, date_ in data_list]
        if len(data_list) < self.limit:
            self.button_next.set_sensitive(False)
        if self.offset == 0:
            self.button_pre.set_sensitive(False)
        if data_list:
            self.offset += self.limit
    
    def set_limit(self, limit):
        self.new_limit = limit

    def validate_request(self):
        if self.offset < 0:
            self.offset = 0
        if self.limit <= 0:
            self.limit = 1

    def on_close(self, widget=None, other=None):
        """"""
        self.destroy()




