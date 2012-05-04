import gtk
import gobject

import traceback
import gettext #internationalization
import locale
import os #usado en start_download
import logging #registro de errores, van a consola y al fichero de texto.
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
#from core.Container_Extractor import Container
from core.config import config_parser
from core.events import events
from core.api import api
import core.cons as cons

#Gui stuff
import media_gui as media
import addons_gui
#tabs
from list_gui import List #lista de descargas activas, pausadas, y finalizadas.
from add_downloads_gui import AddDownloads
from log_gui import Log
#
import gui.main_loop as main_loop
from statusbar_gui import StatusBar
from accounts_gui import ConfigAccounts #ventana/dialog para configurar cuentas premium
from about_gui import AboutGui
from dlg_gui import DlgGui #Dialog
from menu_gui import Menu
#from custom_signals import ChangeIPSig #deprecated
from notebook_gui import Notebook
from preferences.preferences_gui import Preferences


MIN_WIDTH = 550
MIN_HEIGHT = 250
WIDGET, TITLE, CALLBACK, SENSITIVE = range(4)

def init_gettext():
    """Internationalization"""
    #locale_langs = [lang for lang in os.listdir(cons.LOCALE_PATH) if os.path.isdir(os.path.join(cons.LOCALE_PATH, lang))]
    #supported_langs = [lang.split("/")[-3] for lang in gettext.find(cons.APP_NAME, cons.LOCALE_PATH, all=True)] #locale_langs, all=True)]
    lc, encoding = locale.getdefaultlocale()
    default_lang = lc.split("_")[0]
    #default_lang = "ro"
    #default_lang = lc.replace("_", "-").lower()
    #if default_lang not in supported_langs:
        #for lang in supported_langs:
            #if lang.split("-")[0] == default_lang.split("-")[0]:
                #default_lang = lang
                #break
    lang = gettext.translation(cons.APP_NAME, cons.LOCALE_PATH, languages=[default_lang, ], fallback=True)
    lang.install(cons.APP_NAME, cons.LOCALE_PATH) #install _() on builtins namespace

#Catch Unhandled Exceptions...
def excepthook(exc_type, exc_value, tb):
    """"""
    message = "Unhandled exception: "
    message += "".join(traceback.format_exception(exc_type, exc_value, tb))
    logger.critical(message)
    halt()

#and close GUI.
def halt():
    """
    TODO: Mostrar ventana de error y cerrar apropiadamente.
    """
    for window in gtk.window_list_toplevels():
        if isinstance(window, Gui):
            window.on_close()
        window.hide()


class Gui(gtk.Window):
    """
    TODO: aniadir comentarios a cada metodo.
    TODO Create gui api.
    """
    def __init__(self):
        """"""
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        self.set_title(cons.APP_TITLE)
        self.set_size_request(MIN_WIDTH, MIN_HEIGHT)
        self.set_position(gtk.WIN_POS_CENTER)
        self.resize(600, 300)
        
        self.config = config_parser #config.py
        
        #app window position and size
        x, y, w, h = self.config.get_window_settings()
        if gtk.gdk.screen_width() <= w or gtk.gdk.screen_height() <= h:
            self.maximize()
        elif w >= MIN_WIDTH or h >= MIN_HEIGHT:
            self.resize(w, h)
        if x >= 0 and y >= 0:
            self.move(x, y)
        
        #widgets for tabs.
        self.downloads_list_gui = List(parent=self)
        self.downloads_list_gui.treeView.get_selection().connect("changed", self.on_selected)
        self.add_downloads_gui = AddDownloads(self.downloads_list_gui, parent=self)
        self.addons_gui = addons_gui.AddonsManager(self)
        self.preferences = Preferences(self.addons_gui.addons_list)
        self.log_gui = Log()

        self.vbox = gtk.VBox()
        self.add(self.vbox)

        #toolbar. button = ToolButton(icon, label), handler, sensitive.
        #add_download = gtk.ToolButton(gtk.ToolButton(gtk.STOCK_ADD), "Add Download"), self.add_links, True
        stop = (gtk.ToolButton(media.get_image(media.STOP, media.MEDIUM), None), _("Stop Download"), self.stop_download, False) #tuple
        start = (gtk.ToolButton(media.get_image(media.START, media.MEDIUM), None), _("Start Download"), self.start_download, False)
        accounts = (gtk.ToolButton(media.get_image(media.ACCOUNTS, media.MEDIUM), None), _("Accounts"), self.accounts_app, True)
        preferences = (gtk.MenuToolButton(media.get_image(media.PREFERENCES, media.MEDIUM), None), _("Preferences"), self.on_preferences, True)
        about = (gtk.ToolButton(media.get_image(media.ABOUT, media.MEDIUM), None), _("About"), self.about_dlg, True)
        self.stop = stop[WIDGET] #self.stop = gtk.ToolButton(gtk.ToolButton(gtk.STOCK_STOP), "Stop Download"). Para poder cambiar el set_sensitive
        self.start = start[WIDGET]
        self.Toolbar = Toolbar([start, stop, None, accounts, preferences, None, about]) #los botones se agregan al Toolbar en el orden de esta lista. None = separador
        self.vbox.pack_start(self.Toolbar, False)
        
        #menu
        config_preferences = (gtk.MenuItem(), _("Preferences"), self.on_preferences)
        config_about = (gtk.MenuItem(), _("About"), self.about_dlg)
        #addons-menu
        menu_items = [menu_item for menu_item in [addon.get_menu_item() for addon in self.addons_gui.addons_list] if menu_item is not None]
        menu_items.extend([None, config_preferences, config_about])
        menu = Menu(menu_items)
        preferences[WIDGET].set_menu(menu)
        
        #Sessions
        self.load_session()
        
        #tabs (notebooks)
        self.vbox2 = gtk.VBox()
        
        self.notebook = Notebook()
        self.notebook.set_tab_pos(gtk.POS_BOTTOM) #weird butg in gtk+ 2.24.10 on resizing to often (make the app crash).
        self.notebook.set_show_border(False)
        self.notebook.append_page(self.downloads_list_gui, gtk.Label(_("Downloads")))
        self.notebook.append_page(self.add_downloads_gui, gtk.Label(_("Add downloads")))
        [self.notebook.append_page(tab, gtk.Label(addon.name)) for tab, addon in [(addon.get_tab(), addon) for addon in self.addons_gui.addons_list] if tab is not None]
        self.notebook.append_page(self.log_gui, gtk.Label(_("Log")))
        self.notebook.connect("switch-page", self.on_tab_switch)
        
        self.vbox2.pack_start(self.notebook)
        self.vbox.pack_start(self.vbox2)
        
        #status bar
        self.status_bar = StatusBar(self.add_downloads_gui)
        #self.pack_start(self.status_bar, False, False, 0)
        self.vbox.pack_start(self.status_bar, False, False)
        
        #Quit Event
        events.connect(cons.EVENT_QUIT, self.on_close)
        
        #self.connect("destroy", self.on_close) #boton cerrar de la barra de arriba
        self.connect("delete-event", self.on_quit)
        
        self.show_all()

    def on_tab_switch(self, notebook, page, page_num):
        """"""
        previous_page_num = notebook.get_current_page()
        previous_tab_child = notebook.get_nth_page(previous_page_num)
        if previous_tab_child in (self.preferences, ):
            previous_tab_child.on_close()
        elif previous_tab_child in [tab for tab in [addon.get_tab() for addon in self.addons_gui.addons_list] if tab is not None]:
            previous_tab_child.on_close()
        
        current_tab_child = notebook.get_nth_page(page_num) #get child widget in tab.
        if current_tab_child in (self.log_gui, self.preferences):
            current_tab_child.on_load()
        elif current_tab_child in [tab for tab in [addon.get_tab() for addon in self.addons_gui.addons_list] if tab is not None]:
            current_tab_child.on_load()

    def addons_save(self):
        """"""
        [addon.save() for addon in self.addons_gui.addons_list]

    def load_session(self):
        """"""
        api.load_session()
        self.downloads_list_gui.store_items(api.get_stopped_downloads().values())

    def save_session(self):
        """"""
        iditem_list = self.downloads_list_gui.treeView.get_id_item_list()
        api.save_session(iditem_list)

    def stop_download(self, widget):
        """
        TODO: Desactivar boton stop cuando finaliza la descarga seleccionada. *arreglo temporal
        Solucion: pasarle el boton de stop a List, y desactivarlo desde get_status, si th.finished == True.
        TODO: Stop y start deberian ser metodos de list_gui
        """
        model, rows = self.downloads_list_gui.treeView.get_selection().get_selected_rows() #atributo treeView de la clase List
        if rows:
            for row in rows:
                id_item = model[row][0]
                stopped = api.stop_download(id_item) #return true or false
                if stopped:
                    if model[row][1] == self.downloads_list_gui.icons_dict[cons.STATUS_QUEUE]:
                        model[row][1] = self.downloads_list_gui.icons_dict[cons.STATUS_STOPPED]
                    self.stop.set_sensitive(False) #deshabilitar el boton de stop ya que acaban de detener la descarga.
                    self.start.set_sensitive(True)

    def start_download(self, widget):
        """"""
        model, rows = self.downloads_list_gui.treeView.get_selection().get_selected_rows() #atributo treeView de la clase List
        if rows:
            #id_item = model[row][0]
            for row in rows:
                id_item = model[row][0]

                #TODO: Implementar lo mismo pero para stopped (buscar en lista stopped y finished para comparar)
                started = api.start_download(id_item) #return true or false
                if started:
                    model[row][1] = self.downloads_list_gui.icons_dict[cons.STATUS_QUEUE] #status
                    model[row][12] = None #status_msg
                    self.stop.set_sensitive(True) #deshabilitar el boton de stop ya que acaban de detener la descarga.
                    self.start.set_sensitive(False)
                
            self.downloads_list_gui.get_status() #iniciar update de lista.
            iditem_list = self.downloads_list_gui.treeView.get_id_item_list()
            api.reorder_queue(iditem_list)

    def accounts_app(self, widget=None):
        """"""
        config_accounts = ConfigAccounts(parent=self) #instancia de clase. ConfigAccounts()

    def on_preferences(self, widget=None):
        """"""
        #self.preferences = Preferences() #add in the __init__ class
        index_page = self.notebook.page_num(self.preferences) #get the page containig the widget
        if index_page >= 0: #if = -1 there is not such tab.
            self.notebook.set_current_page(index_page)
        else:
            self.notebook.insert_closable_page(self.preferences, gtk.Label(_("Preferences")))
            self.notebook.set_current_page(-1)
        #PreferencesDlg(parent=self)

    def about_dlg(self, widget=None):
        """"""
        about_dlg = AboutGui(parent=self)

    def on_selected(self, widget):
        """
        Activa o desactiva los botones de comenzar y detener, dependiendo de que archivo se selecciono.
        Posiblemente seria mejor implementar este metodo en la clase List, pero habria que pasarle los botones que cambiaran de estado.
        TODO: para modificar los multiples seleccionados, se necesita transformar rows en un treerowreference, ver docs del get_selected_rows.
        """
        #model, rows = self.list_gui.treeView.get_selection().get_selected_rows()
        model, rows = widget.get_selected_rows()
        self.stop.set_sensitive(False)
        self.start.set_sensitive(False)
        
        if len(rows) == 1: #single selection.
            row = rows[0]
            id_item = model[row][0] # model[rows[row]]
            #self.list_gui.row_selected = model[row] #actualizar atributo del list_gui con el row seleccionado.
            self.stop.set_sensitive(True)
            self.start.set_sensitive(False)
            #self.start.set_icon_widget(gtk.ToolButton(gtk.STOCK_MEDIA_STOP))
            #if file_name in [download_item.name for download_item in self.downloadmanager.stopped_downloads + self.downloadmanager.complete_downloads]:
            stopped_downloads = api.get_stopped_downloads()
            try:
                item = stopped_downloads[id_item]
                self.stop.set_sensitive(False)
                self.start.set_sensitive(True)
            except KeyError:
                pass
        elif rows: #multi selection
            self.stop.set_sensitive(True)
            self.start.set_sensitive(True)
            #self.statusbar.push(0, file_name) #poner el nombre de archivo en la barra de abajo.
    
    def on_quit(self, widget=None, other=None):
        """"""
        if api.get_active_downloads():
            message = _("ochDownload still has some active downloads. Do you want to quit anyway?")
            m = DlgGui(self, gtk.STOCK_DIALOG_WARNING, _("Active Downloads"), message, True, True)
            if m.accepted:
                self.on_close()
            else:
                return True
        else:
            self.on_close()
    
    def on_close(self, widget=None, other=None):
        """"""
        x, y = self.get_position() #si hay un error unhandled se puede obtener la posicion y tamanio de ventana?
        w, h = self.get_size()
        try:
            self.hide_all()
            self.save_session()
            self.addons_save()
            self.destroy()
            #gtk.main_quit()
            main_loop.quit()
            self.config.set_window_settings(x, y, w, h)
            self.config.save_config()
        except Exception as err:
            logger.exception(err)
        #SMTPLogger(cons.LOG_FILE).start() #start send_log in new thread - DEPRECATED -


class Toolbar(gtk.Toolbar):
    """"""
    def __init__(self, btn_list):
        """
        list = [(tool_name, image, module_handler), ]
        """
        gtk.Toolbar.__init__(self)
        self.set_style(gtk.TOOLBAR_ICONS) #gtk.TOOLBAR_BOTH = icono + imagen
        self.set_icon_size(gtk.ICON_SIZE_LARGE_TOOLBAR)
        for button in btn_list:
            if button is None:
                item = gtk.SeparatorToolItem()
            else:
                item = button[WIDGET] #eg: gtk.ToolButton(gtk.STOCK_NEW), "Add Download"
                item.set_label(button[TITLE])
                item.connect("clicked", button[CALLBACK]) #eg: item.connect("clicked",  self.add_links)
                item.set_sensitive(button[SENSITIVE])
            self.insert(item, -1) #-1 = insertar al final


if __name__ == "__main__":
        import gui.main_loop as main_loop
        #from gui.main_gui import Gui, excepthook, halt, init_gettext
        
        sys.excepthook = excepthook #capturar exceptiones unhandled.
        warnings.showwarning = self.redirect_warnings #capturar pygtk warnings.
        init_gettext() #internacionalization
        try:
            #select ms-windows theme (pyinstaller 1.5.1 fix)
            if cons.OS_WIN:
                try:
                    basedir = os.environ['_MEIPASS2']
                    gtkrc = os.path.join(basedir, 'share/themes/MS-Windows/gtk-2.0/gtkrc')
                    gtk.rc_set_default_files([gtkrc])
                    gtk.rc_reparse_all_for_settings(gtk.settings_get_default(), True)
                except KeyError as err:
                    #self.logger.warning(err)
                    pass
            #
            #self.logger.info("New app gui instance")
            gobject.threads_init() #permitir threading en pygtk
            
            gui_istance = Gui()
            main_loop.run()

        except Exception as err:
            #self.logger.exception(err)
            halt() #close gui.
