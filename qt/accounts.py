import logging
logger = logging.getLogger(__name__)

#Libs
from core.host_accounts import host_accounts
from core.plugins_parser import plugins_parser

from PySide.QtGui import *
from PySide.QtCore import *

from list_model import SimpleListModel


ACCOUNT_ID, HOST, STATUS, USER, PASSWORD, ENABLE = range(6)


class ConfigAccounts(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setWindowTitle(_('Host Accounts'))
        self.resize(500, 450)
        
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        
        # ####################### #
        
        vbox_accounts = QVBoxLayout()
        group_accounts = QGroupBox(_('Accounts:'))
        group_accounts.setLayout(vbox_accounts)
        
        self.tree_view = QTreeView(parent)
        #
        #listview look
        self.tree_view.setWordWrap(True) #search textElideMode
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setIndentation(0)
        self.tree_view.setAlternatingRowColors(True)
        #
        self.items = []
        headers = ["hidden_id_account", _("Host"), _("Status"), _("Username"), _("Password"), _("Enable")]
        bool_cols = [ENABLE, ]
        #
        self.__model = SimpleListModel(headers, self.items, bool_cols)
        self.tree_view.setModel(self.__model)
        vbox_accounts.addWidget(self.tree_view)
        
        self.tree_view.setColumnHidden(0, True)
        
        hbox_accounts = QHBoxLayout()
        hbox_accounts.addStretch(0) #stretch/align widget to right.
        vbox_accounts.addLayout(hbox_accounts)
        
        self.btn_remove = QPushButton(_('Remove'))
        self.btn_remove.clicked.connect(self.on_remove)
        self.btn_remove.setFixedHeight(35)
        self.btn_remove.setMaximumWidth(80)
        self.btn_remove.setEnabled(False)
        hbox_accounts.addWidget(self.btn_remove)
        
        self.btn_check = QPushButton(_('Check'))
        self.btn_check.clicked.connect(self.on_check)
        self.btn_check.setFixedHeight(35)
        self.btn_check.setMaximumWidth(80)
        self.btn_check.setEnabled(False)
        hbox_accounts.addWidget(self.btn_check)
        
        vbox.addWidget(group_accounts)
        
        # ####################### #
        
        vbox_login = QVBoxLayout()
        group_login = QGroupBox(_('Login:'))
        group_login.setLayout(vbox_login)
        
        label_server = QLabel(_('Server:'))
        #label_server.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label_user = QLabel(_('Username:'))
        label_pass = QLabel(_('Password:'))
        
        self.cb = QComboBox()
        [self.cb.addItem(service) for service, plugin_config in sorted(plugins_parser.services_dict.items()) if plugin_config.get_premium_available()]
        self.entry_user = QLineEdit()
        self.entry_pass = QLineEdit()
        
        grid_login = QGridLayout()
        grid_login.addWidget(label_server, 1, 0)
        grid_login.addWidget(self.cb, 1, 1)
        grid_login.addWidget(label_user, 2, 0)
        grid_login.addWidget(self.entry_user, 2, 1)
        grid_login.addWidget(label_pass, 3, 0)
        grid_login.addWidget(self.entry_pass, 3, 1)
        vbox_login.addLayout(grid_login)
        
        hbox_add = QHBoxLayout()
        btn_add = QPushButton(_('Add'))
        btn_add.clicked.connect(self.on_add)
        btn_add.setFixedHeight(35)
        btn_add.setMaximumWidth(80)
        if not self.cb.count():
            btn_add.setEnabled(False)
        hbox_add.addStretch(0)
        hbox_add.addWidget(btn_add)
        vbox_login.addLayout(hbox_add)
        
        vbox.addWidget(group_login)
        
        # ####################### #
        
        vbox.addSpacing(20)
        
        hbox_btns = QHBoxLayout()
        hbox_btns.addStretch()
        
        btn_cancel = QPushButton(_('Cancel'))
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setFixedHeight(35)
        btn_cancel.setMaximumWidth(80)
        hbox_btns.addWidget(btn_cancel)
        
        btn_accept = QPushButton(_('Accept'))
        btn_accept.clicked.connect(self.on_accept)
        btn_accept.setDefault(True)
        btn_accept.setFixedHeight(35)
        btn_accept.setMaximumWidth(80)
        hbox_btns.addWidget(btn_accept)
        
        vbox.addLayout(hbox_btns)
        
        # ####################### #

        #self.tree_view.selectionModel().selectionChanged.connect(self.on_selected)
        
        self.load_accounts()
        
        self.timer = parent.idle_timeout(1000, self.update_)
        
        #self.show()
        self.exec_()
        self.deleteLater()
    
    def get_selected_row(self):
        """"""
        selected_row = self.tree_view.selectionModel().selectedRows()[0].row()
        return selected_row
    
    #def on_selected(self, selected, unselected):
        #""""""
        #todo: heredar treeView y subclass selectionChanged
        #row = self.get_selected_row()
        #self.btn_remove.setEnabled(True)
        #self.btn_check.setEnabled(True)
    
    def load_accounts(self):
        accounts_list = [account
                        for service, accounts_list in sorted(host_accounts.accounts_dict.items())
                        for account in accounts_list]
        for account in accounts_list:
            password = "".join(["*" for _ in account.password])
            self.__model.append([account.id_account, account.host, account.status, account.username, password, account.enable])
            #TODO: Automatic accounts checking on load.
    
    def on_accept(self):
        for row in self.items:
            host_accounts.enable_account(row[HOST], row[ACCOUNT_ID], row[ENABLE])
        host_accounts.save_accounts()
        self.timer.stop()
        self.done(0)
    
    def on_add(self):
        username = self.entry_user.text()
        password = self.entry_pass.text()
        if username and password:
            account_item = host_accounts.create_account_item(self.cb.currentText(), username, password) #error, since we didnt check it, yet.
            self.__model.clear()
            self.load_accounts()
            host_accounts.start_checking(account_item.host, account_item.id_account)
    
    def on_remove(self):
        row = self.get_selected_row()
        host_accounts.remove_account(self.items[row][HOST], self.items[row][ACCOUNT_ID])
        self.__model.remove(row)
    
    def on_check(self):
        row = self.get_selected_row()
        host_accounts.start_checking(self.items[row][HOST], self.items[row][ACCOUNT_ID])
    
    def update_(self):
        account_list = host_accounts.get_checking_update()
        for account_item in account_list:
            for row in self.items:
                if row[ACCOUNT_ID] == account_item.id_account:
                    row[STATUS] = account_item.status

    def reject(self, *args, **kwargs):
        #reimplemented.
        host_accounts.revert_changes()
        self.timer.stop()
        self.hide()
        QDialog.reject(self, *args, **kwargs)
