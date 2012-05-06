import uuid
import cookielib
import os
import threading
import pickle #permite escribir diccionarios, listas, etc en archivos, preservando el tipo.
import importlib
import copy
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

from network.connection import URLOpen, URLClose
import cons
import events

#COOKIE_CONNECTION_RETRY = 3
HOST, STATUS, USER, PASSWORD, ENABLE = range(5) #Cool stuff.
PATH_FILE = os.path.join(cons.APP_PATH, "accounts")


class AccountItem:
    """"""
    def __init__(self, host, username, password, status=None, enable=False):
        """"""
        self.id_account = str(uuid.uuid1()) #id unico.
        self.host = host
        self.username = username
        self.password = password
        self.status = status
        self.enable = enable


class _HostAccounts:
    """"""
    def __init__(self):
        """
        TODO: Refactory.
        """
        #self.list_accounts_services = [] #Lista de host de las cuentas activas.
        self.accounts_dict = {}#{host: [account_item, ], }
        self.tmp_accounts_dict = {}#{host: [account_item, ], } revert changes on cancel.
        self.thread_checking_accounts = {} #{id_account: (th, account_item), }
        self.load_accounts()
        logger.debug("Host Accounts instanced.")

    def get_account(self, service): #has premium
        """"""
        for account_item in self.accounts_dict.get(service, []):
            if account_item.enable and account_item.status == cons.ACCOUNT_PREMIUM:
                return account_item
        return None

    def add_account_item(self, account_item):
        """"""
        accounts_list = self.accounts_dict.get(account_item.host, [])
        accounts_list.append(account_item)
        self.accounts_dict[account_item.host] = accounts_list

    def create_account_item(self, host, username, password):
        """"""
        account_item = AccountItem(host, username, password)
        self.add_account_item(account_item)
        return account_item
    
    def get_cookie(self, url, dict_form, headers=None): #DEPRECATED
        """
        Uso:
        if cookie is not None:
            #connection success
            if cookie:
                #login success
            else:
                #login fail
        else:
            #server down
        """
        #for retry in range(COOKIE_CONNECTION_RETRY):
        try:
            cookie = cookielib.CookieJar()
            with URLClose(URLOpen(cookie).open(url, dict_form, headers=headers)) as s: #eg: url= login-url, data = {"login": "1", "redir": "1", "username": user, "password", password}
                opener = s
        except Exception, err: #this only happen on http error, not bad-login, etc.
            logger.warning(err)
            #host_down = True
        else:
            return cookie
        return None #cant connect.

    def load_accounts(self):
        """
        Cargar cuentas desde fichero.
        """
        try:
            with open(PATH_FILE, "rb", cons.FILE_BUFSIZE) as fh:
                list_accounts = pickle.load(fh)
                for list_item in list_accounts[:]:
                    account_item = AccountItem(list_item[HOST], list_item[USER], list_item[PASSWORD], list_item[STATUS], list_item[ENABLE])
                    self.add_account_item(account_item)
                self.tmp_accounts_dict = copy.deepcopy(self.accounts_dict) #revert changes on cancel
        except (EnvironmentError, pickle.UnpicklingError) as err:
            logger.info("Accounts file doesnt exists: {0}".format(err))
        except EOFError as err:
            logger.warning("End of file error: {0}".format(err))
        except Exception as err:
            logger.exception(err)

    def save_accounts(self):
        """
        Save accounts from list to file (it'll erase the file).
        """
        #del self.list_accounts_services[:] #eliminar contenido de la lista.
        accounts = [] #[[user, pass, ...], ]
        try:
            with open(PATH_FILE, "wb", cons.FILE_BUFSIZE) as fh: #w reemplaza el contenido del archivo.
                for accounts_list in self.accounts_dict.values():
                    for account_item in accounts_list:
                        if account_item.status != cons.ACCOUNT_PREMIUM:
                            account_item.enable = False
                        if account_item.status == cons.ACCOUNT_CHECKING:
                            status = cons.ACCOUNT_ERROR
                        else:
                            status = account_item.status
                        accounts.append([account_item.host, status, account_item.username, account_item.password, account_item.enable])
                pickle.dump(accounts, fh, pickle.HIGHEST_PROTOCOL)
                self.tmp_accounts_dict = copy.deepcopy(self.accounts_dict) #revert changes on cancel
        except (EnvironmentError, pickle.PicklingError) as err:
            logger.warning("Can't save the account: {0}".format(err))

    def remove_account(self, service, account_item_id):
        """"""
        accounts_list = self.accounts_dict.get(service, [])
        for account_item in accounts_list[:]:
            if account_item.id_account == account_item_id:
                accounts_list.remove(account_item)
                self.accounts_dict[service] = accounts_list
                return True

    def enable_account(self, service, account_item_id, enable, save_changes=False):
        """"""
        for account_item in self.accounts_dict.get(service, []):
            if account_item.id_account == account_item_id:
                account_item.enable = enable
        if save_changes: #method called from plugin_bridge.
            self.save_accounts()
    
    def revert_changes(self):
        """"""
        self.accounts_dict = copy.deepcopy(self.tmp_accounts_dict) #revert changes on cancel
    
    #////////////////////////////////////////
    
    def start_checking(self, service, account_item_id):
        """"""
        for account_item in self.accounts_dict.get(service, []):
            if account_item.id_account == account_item_id and account_item.status != cons.ACCOUNT_CHECKING:
                account_item.status = cons.ACCOUNT_CHECKING
                th = threading.Thread(group=None, target=self.account_checking, name=None, args=(account_item, ))
                self.thread_checking_accounts[account_item.id_account] = (th, account_item)
                th.start()

    def account_checking(self, account_item):
        """"""
        try:
            module = importlib.import_module("plugins.{0}.premium_download".format(account_item.host))
        except ImportError as err:
            account_item.status = cons.ACCOUNT_ERROR
            logger.info("{0}".format(err))
        else:
            premium_download = module.PremiumDownload(None, None, username=account_item.username, password=account_item.password)
            cookie = premium_download.get_cookie()
            account_status = premium_download.get_account_status(cookie)
            if account_status not in (cons.ACCOUNT_PREMIUM, cons.ACCOUNT_FREE):
                account_item.status = cons.ACCOUNT_ERROR
            else:
                account_item.status = account_status

    def get_checking_update(self):
        """"""
        TH, ACCOUNT_ITEM = range(2)
        result_list = []
        for id_account, values in self.thread_checking_accounts.items():
            account_item = values[ACCOUNT_ITEM]
            result_list.append(account_item)
            th = values[TH]
            if not th.is_alive():
                del self.thread_checking_accounts[id_account]
        return result_list


#modules are singletons in python :)
host_accounts = _HostAccounts() #make it global.
