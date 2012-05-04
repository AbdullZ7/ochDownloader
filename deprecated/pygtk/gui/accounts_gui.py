#Crear un paquete "config" con este modulo y los q vayan a ir en la configuracion. (pestanias?)

import gtk
import gobject

import importlib
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
import core.cons as cons
from core.host_accounts import host_accounts
from core.plugins_parser import plugins_parser

from dialog_base import Dialog

ACCOUNT_ID, HOST, STATUS, USER, PASSWORD, ENABLE = range(6) #Cool stuff.


class ConfigAccounts(Dialog):
    """
    Status is always Premium or Free, wont save the account on status error.
    If we get error on re-check, it wont modify the previous status (premium or free).
    """
    def __init__(self, parent=None):
        """"""
        Dialog.__init__(self)
        self.set_title(_("Host Accounts"))
        self.set_size_request(500, 500)
        self.set_transient_for(parent)
        
        self.host_accounts = host_accounts #instancia de clase Host_Accounts
        self.update_flag = False
        self.stop_update = False
        
        #Estructura-General:
        #-------------------vbox1_start---------------
        #-------------------hbox1_start---------------
        #-------------------frame2----------------------Accounts
        #-------------------hbox1_end----------------
        #-------------------hbox3_start--------------
        #-------------------frame3----------------------Login
        #-------------------hbox3_end----------------
        #-------------------hbox6-----------------------Exit-Buttons
        #-------------------vbox1_end----------------
        
        #Estructura-Accounts
        #-------------------frame2_start-------------
        #-------------------vbox3_start--------------
        #---------------------------------------------------ScrollWindow
        #-------------------hbox2-----------------------Buttons
        #-------------------vbox3_end----------------
        #-------------------frame2_end---------------
        
        #Estructura-Login
        #-------------------frame3_start-------------
        #-------------------vbox4_start--------------
        #-------------------hbox4_start--------------
        #-------------------vbox5-----------------------Label
        #-------------------vbox6-----------------------Entry
        #-------------------hbox4_end----------------
        #-------------------hbox5-----------------------Button
        #-------------------vbox4_end----------------
        #-------------------frame3_end---------------
        
        
        #containers-separators.
        #self.vbox no puede ser cambiado en gtk.Dialog. Crear variable vbox y luego meterla en self.vbox.
        vbox1 = gtk.VBox(False, 20) #gtk.VBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio vertical entre hijos.
        vbox1.set_border_width(10) #outside-space
        
        #vbox1_start
        #hbox1_start
        #-------------------------------------------
        #containers-separators.
        hbox1 = gtk.HBox(False, 10) #file field and button examine.
        #gtk.HBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio horizontal entre hijos.
        
        #Accounts list
        #frame2
        frame2 = gtk.Frame(_("Accounts:"))
        
        #vbox3
        #containers-separators.
        vbox3 = gtk.VBox(False, 10)
        vbox3.set_border_width(10) #outside-space
        hbox2 = gtk.HBox(False, 10) #Buttons.
        
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.store = gtk.ListStore(str, str, str, str, str, bool)#modelo de columnas. (3 columnas de strings)
        
        #arma el cuadro con los items
        self.treeView = gtk.TreeView(self.store)
        self.treeView.set_rules_hint(True) #turna el color de los items, creo.
        scroll.add(self.treeView)
        
        self.row_selected = None #fila seleccionada, se cambia en el on_selected
        self.treeView.get_selection().connect("changed", self.on_selected) #item seleccionado
        
        
        #Columns item names.
        col_list = ["hidden_id_account", _("Host"), _("Status"), _("Username"), _("Password"), _("Enable")] #podria usar un frozenset, no se si lo soporta cython.
        self.create_columns(col_list)
        
        check_btn = gtk.CheckButton()
        check_btn.set_active(True)
        #check_btn.unset_flags(gtk.CAN_FOCUS)
        
        #self.store.append(["YES", "CRAP", "CRAP", "premium", False]) 
        
        vbox3.add(scroll)
        
        #hbox2
        self.button1 = gtk.Button(_("Remove"))
        self.button1.set_size_request(80, 35)
        self.button1.set_sensitive(False)
        self.button1.connect("clicked", self.on_remove)
        hbox2.add(self.button1)
        
        self.button2 = gtk.Button(_("Check"))
        self.button2.set_size_request(80, 35)
        self.button2.set_sensitive(False)
        self.button2.connect("clicked", self.on_check)
        hbox2.add(self.button2)
        
        halign1 = gtk.Alignment(1, 0, 0, 0) #horizontal container. right liagment.
        #xalign: espacio libre a la izquierda del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        #yalign: espacio libre vertical arriba del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        halign1.add(hbox2)
        
        vbox3.pack_start(halign1, False)
        
        #Let's pack.
        frame2.add(vbox3)
        hbox1.add(frame2)
        vbox1.pack_start(hbox1)
        #vbox.pack_start(child, expand=True, fill=True, padding=0)
        #-------------------------------------------
        #hbox1_end
        
        #hbox3_start
        #-------------------------------------------
        #containers-separators.
        hbox3 = gtk.HBox(False, 10) #buttons
        #gtk.HBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio horizontal entre hijos.
        
        #Login fields
        #frame3
        frame3 = gtk.Frame(_("Login:"))
        
        #vbox4
        #containers-separators.
        vbox4 = gtk.VBox(False, 10) #container
        vbox4.set_border_width(10) #outside-space
        vbox5 = gtk.VBox(False, 10) #label
        vbox6 = gtk.VBox(False, 10) #entry
        hbox4 = gtk.HBox(False, 10) #entry+label
        hbox5 = gtk.HBox(False, 10) #buttons
        
        #hbox4
        #vbox5
        
        label_server = gtk.Label(_("Server:"))
        label_server.set_alignment(0, 0.5) #set_alignment(xalign, yalign), 0=left, 0.5=middle
        vbox5.add(label_server)
        label1 = gtk.Label(_("Username:"))
        label1.set_alignment(0, 0.5) #set_alignment(xalign, yalign), 0=left, 0.5=middle
        vbox5.add(label1)
        label2 = gtk.Label(_("Password:"))
        label2.set_alignment(0, 0.5) #set_alignment(xalign, yalign), 0=left, 0.5=middle
        vbox5.add(label2)
        
        hbox4.pack_start(vbox5, False)
        
        #vbox6
        self.cb = gtk.combo_box_new_text() #dropdow menu
        #cb.connect("changed", self.on_changed")
        premium_services = [service for service, plugin_config in plugins_parser.services_dict.items() if plugin_config.get_premium_available()]
        for service in sorted(premium_services):
            self.cb.append_text(service)
        self.cb.set_active(0)
        
        vbox6.add(self.cb)
        
        #entry...
        self.entry1 = gtk.Entry()
        self.entry1.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.entry1.set_width_chars(40) #entry width
        
        vbox6.add(self.entry1)
        
        #entry...
        self.entry2 = gtk.Entry()
        self.entry2.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.entry2.set_width_chars(40) #entry width
        
        vbox6.add(self.entry2)
        
        hbox4.add(vbox6)
        
        vbox4.add(hbox4)
        
        #hbox5
        button3 = gtk.Button(_("Add"))
        button3.set_size_request(80, 35)
        button3.connect("clicked", self.on_add)
        hbox5.add(button3)
        
        
        halign2 = gtk.Alignment(1, 0, 0, 0) #horizontal container. right liagment.
        #xalign: espacio libre a la izquierda del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        #yalign: espacio libre vertical arriba del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        halign2.add(hbox5)
        
        vbox4.add(halign2)
        
        #Let's pack.
        frame3.add(vbox4)
        hbox3.add(frame3)
        vbox1.pack_start(hbox3, False)
        #vbox.pack_start(child, expand=True, fill=True, padding=0)
        #-------------------------------------------
        #hbox3_end
        
        #buttom.
        #-------------------------------------------
        #containers-separators.
        hbox6 = gtk.HBox(False, 10) #buttons
        #gtk.HBox(homogeneous=False, spacing=0) homogeneous: mismo espacio cada hijo, spacing: espacio horizontal entre hijos.
        
        #hbox6
        button4 = gtk.Button(_("Cancel"))
        button4.set_size_request(80, 35)
        button4.connect("clicked", self.on_close)
        hbox6.add(button4)
        
        button5 = gtk.Button(_("Done"))
        button5.set_size_request(80, 35)
        button5.connect("clicked", self.on_done)
        hbox6.add(button5)
        
        halign3 = gtk.Alignment(1, 0, 0, 0) #horizontal container. right liagment.
        #xalign: espacio libre a la izquierda del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        #yalign: espacio libre vertical arriba del hijo. 0.0 = sin espacio arriba. 1.0 = todo el espacio arriba.
        halign3.set_padding(15, 0, 0, 0) #set_padding(top, bottom, left, right)
        halign3.add(hbox6)
        
        vbox1.pack_start(halign3, False)
        #vbox.pack_start(child, expand=True, fill=True, padding=0)
        #-------------------------------------------
        #vbox1_end
        
        
        self.connect("response", self.on_close)
        self.vbox.pack_start(vbox1)
        
        #cargar cuentas.
        if self.cb.get_active_text() is not None:
            self.load_accounts()
        else:
            button3.set_sensitive(False)
        
        self.start_update()
        
        self.show_all()
        self.run()
        
        
    def create_columns(self, col_list):
        """
        Crea las columnas de la lista
        """
        for item in col_list:
            id_col = col_list.index(item)
            if item != _("Enable"):
                rendererText = gtk.CellRendererText() #pide el primer item que ira en la columna (text=0) o segundo, etc...
                rendererText.set_property("ellipsize", 3) #2= middle, 3 = right, 1 = left
                column = gtk.TreeViewColumn(item, rendererText, text=id_col)
                column.set_resizable(True)
                column.set_expand(True)
                if item == "hidden_id_account":
                    column.set_visible(False)
            else:
                rendererToggle = gtk.CellRendererToggle()
                #rendererToggle.set_property('activatable', True)
                column = gtk.TreeViewColumn(item, rendererToggle)
                column.add_attribute(rendererToggle, 'active', id_col)
                rendererToggle.connect("toggled", self.on_toggled, id_col)
            
            column.set_min_width(1)
            column.set_sort_column_id(id_col) #ordenar columna
            self.treeView.append_column(column)

    def load_accounts(self):
        """
        Mostrar cuentas en el cuadro "Accounts". username, password y enable.
        """
        accounts_list = [account
                        for service, accounts_list in sorted(self.host_accounts.accounts_dict.items())
                        for account in accounts_list]
        for account in accounts_list:
            password = "".join(["*" for x in account.password])
            self.store.append([account.id_account, account.host, account.status, account.username, password, account.enable])
            #TODO: Automatic accounts checking on load.
    
    def on_toggled(self, celltoggled, path, id_col):
        """"""
        model = self.treeView.get_model()
        if celltoggled.get_active(): #devuelve True, si el check estaba activado, sino false.
            model[path][id_col] = False
        else:
            #for row in model: #desactivar los otros antes de activar este.
                #row[id_col] = False
            model[path][id_col] = True
        self.host_accounts.enable_account(model[path][HOST], model[path][ACCOUNT_ID], model[path][id_col]) #host, user, enable
        #print type(model[path][id_col])

    def on_check(self, widget):
        """"""
        self.host_accounts.start_checking(self.row_selected[HOST], self.row_selected[ACCOUNT_ID])

    def on_selected(self, widget):
        """"""
        model, row = widget.get_selected()
        if row:
            self.row_selected = model[row] #actualizar atributo con el row seleccionado.
            self.button1.set_sensitive(True)
            self.button2.set_sensitive(True)
        else: #si se deselecciono
            self.button1.set_sensitive(False) #remove button
            self.button2.set_sensitive(False) #check button

    def on_remove(self, widget):
        """"""
        self.host_accounts.remove_account(self.row_selected[HOST], self.row_selected[ACCOUNT_ID])
        self.store.remove(self.row_selected.iter) #obeter iter: row.iter

    def on_add(self, widget): #new
        """"""
        username = self.entry1.get_text()
        password = self.entry2.get_text()
        if username and password:
            account_item = self.host_accounts.create_account_item(self.cb.get_active_text(), username, password) #error, since we didnt check it, yet.
            self.entry1.set_text("")
            self.entry2.set_text("")
            self.store.clear()
            self.load_accounts()
            self.host_accounts.start_checking(account_item.host, account_item.id_account)

    def start_update(self):
        """"""
        if not self.update_flag:
            self.update_flag = True
            gobject.timeout_add(1000, self.update_checking_status)

    def update_checking_status(self): #this method steals cycles, its not a new thread
        """"""
        account_list = self.host_accounts.get_checking_update()
        for account_item in account_list:
            for row in self.store:
                if row[ACCOUNT_ID] == account_item.id_account:
                    row[STATUS] = account_item.status
        if self.stop_update:
            return False
        return True #keep it updating,

    def on_done(self, widget):
        """"""
        self.stop_update = True
        self.host_accounts.save_accounts()
        self.destroy()

    def on_close(self, widget, other=None):
        """"""
        self.stop_update = True
        self.host_accounts.revert_changes()
        self.destroy() 
        
        
