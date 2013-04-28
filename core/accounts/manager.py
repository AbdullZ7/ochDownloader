import os
import pickle
import logging
logger = logging.getLogger(__name__)
from collections import OrderedDict

from core import cons
from core.slots import Slots
from item import AccountItem
from checker import AccountChecker

HOST, STATUS, USER, PASSWORD, ENABLE = range(5)
PATH_FILE = os.path.join(cons.APP_PATH, "accounts")


class _AccountManager:
    def __init__(self):
        self.accounts_dict = {} # {host: {id_account: account_item, }, }
        self.thread_checking_accounts = {} # {id_account: th, }
        self.checking_accounts = []
        self.slots = Slots(limit=5)
        self.load()

    def load(self):
        try:
            with open(PATH_FILE, "rb", cons.FILE_BUFSIZE) as fh:
                accounts_list = pickle.load(fh)
                for item in accounts_list:
                    account_item = AccountItem(item[HOST], item[USER], item[PASSWORD], item[STATUS], item[ENABLE])
                    self.add_account_item(account_item)
        except (EnvironmentError, EOFError, pickle.UnpicklingError) as err:
            logger.warning(err)
        except Exception as err:
            logger.exception(err)

    def save(self):
        accounts_list = [] # [[user, pass, ...], ]
        try:
            with open(PATH_FILE, "wb", cons.FILE_BUFSIZE) as fh:
                for accounts in self.accounts_dict.itervalues():
                    for account in accounts.itervalues():
                        accounts_list.append([account.host, account.status, account.username, account.password, account.enable])
                pickle.dump(accounts_list, fh, pickle.HIGHEST_PROTOCOL)
        except (EnvironmentError, pickle.PicklingError) as err:
            logger.warning("Can't save the account: {0}".format(err))

    def add_account_item(self, account_item):
        accounts = self.accounts_dict.get(account_item.host, OrderedDict())
        accounts[account_item.id_account] = account_item
        self.accounts_dict[account_item.host] = accounts

    def get_account_or_none(self, host):
        for account_item in self.accounts_dict.get(host, {}).itervalues():
            if account_item.enable:
                return account_item

    def get_account_as_dict(self, host):
        account = self.get_account_or_none(host)
        if account is not None:
            return {'account_id': account.id_account,
                    'username': account.username,
                    'password': account.password,
                    'status': account.status}

    def new_account(self, host, user, password):
        account = AccountItem(host, user, password)
        self.add_account_item(account)
        self.checking_accounts.append(account)
        self.start_checking()

    def remove_account(self, host, id_account):
        account = self.accounts_dict[host][id_account]
        del self.accounts_dict[host][id_account]
        if not self.accounts_dict[host]:
            del self.accounts_dict[host]
        try:
            self.checking_accounts.remove(account)
            del self.thread_checking_accounts[id_account]
            self.slots.remove_slot()
        except (ValueError, KeyError):
            pass

    def enable_account(self, host, id_account):
        account = self.accounts_dict[host][id_account]
        account.enable = True

    def disable_account(self, host, id_account):
        account = self.accounts_dict[host][id_account]
        account.enable = False

    def manual_checking(self, host, id_account):
        account = self.accounts_dict[host][id_account]
        if account not in self.checking_accounts:
            self.checking_accounts.append(account)

    def start_checking(self):
        for account in self.checking_accounts:
            if self.slots.add_slot():
                th = AccountChecker(account.host, account.username, account.password)
                th.start()
                self.thread_checking_accounts[account.id_account] = th
            else:
                return

    def update(self):
        result = []
        for id_item, th in self.thread_checking_accounts.items():
            if not th.is_alive():
                account = self.accounts_dict[th.host][id_item]
                account.status = th.status
                result.append(account)
                self.checking_accounts.remove(account)
                del self.thread_checking_accounts[id_item]
                self.slots.remove_slot()
                self.start_checking()
        return result


accounts_manager = _AccountManager()