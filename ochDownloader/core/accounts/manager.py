import os
import json
import logging
from collections import OrderedDict

from core import cons
from core.utils.concurrent.thread import Future

from . import worker
from .item import AccountItem, CheckingAccountItem

logger = logging.getLogger(__name__)

HOST, STATUS, USER, PASSWORD, ENABLE = range(5)
PATH_FILE = os.path.join(cons.HOME_APP_PATH, "accounts")


class _AccountManager:

    def __init__(self):
        self.accounts_dict = {}  # {host: {uid: AccountItem, }, }
        self.checking_accounts = {}
        self.pending_accounts = OrderedDict()
        self._active_limit = 5
        self.load()

    def load(self):
        # TODO: move this method to somewhere else
        try:
            with open(PATH_FILE, "r", encoding='utf-8') as fh:
                accounts_list = json.load(fh)
        except Exception as err:
            logger.exception(err)
        else:
            for item in accounts_list:
                account_item = AccountItem(item[HOST], item[USER],
                                           item[PASSWORD], item[STATUS],
                                           item[ENABLE])
                self.add_account_item(account_item)

    def save(self):
        accounts_list = []  # [[user, pass, ...], ]

        for accounts in self.accounts_dict.values():
            for account in accounts.values():
                account_item = [account.host, account.status,
                                account.username, account.password,
                                account.enable]
                accounts_list.append(account_item)

        try:
            with open(PATH_FILE, "w", encoding='utf-8') as fh:
                json.dump(accounts_list, fh)
        except Exception as err:
            logger.exception(err)

    def get_account_or_none(self, host):
        for account_item in self.accounts_dict.get(host, {}).values():
            if account_item.enable:
                return account_item

    def get_account_as_dict(self, host):
        account = self.get_account_or_none(host)

        if account is not None:
            return {
                'account_id': account.uid,
                'username': account.username,
                'password': account.password,
                'status': account.status
            }

    def add_account_item(self, account_item):
        accounts = self.accounts_dict.get(account_item.host, OrderedDict())
        accounts[account_item.uid] = account_item
        self.accounts_dict[account_item.host] = accounts

    def add(self, host, user, password):
        account = AccountItem(host, user, password)
        self.pending_accounts[account.uid] = account
        self.add_account_item(account)
        self.start_checking()

    def remove(self, host, id_account):
        del self.accounts_dict[host][id_account]

        if not self.accounts_dict[host]:
            del self.accounts_dict[host]

        try:
            del self.checking_accounts[id_account]
        except KeyError:
            pass

        try:
            del self.pending_accounts[id_account]
        except KeyError:
            pass

    def enable_account(self, host, id_account):
        account = self.accounts_dict[host][id_account]
        account.enable = True

    def disable_account(self, host, id_account):
        account = self.accounts_dict[host][id_account]
        account.enable = False

    def manual_checking(self, host, id_account):
        account = self.accounts_dict[host][id_account]
        self.pending_accounts[id_account] = account

    def start_checking(self):
        for uid, account in list(self.pending_accounts.items()):
            if len(self.checking_accounts) >= self._active_limit:
                break

            del self.pending_accounts[uid]
            checking = CheckingAccountItem(account)
            checking.thread = Future(target=worker, args=(account.plugin, account.username, account.password))
            self.checking_accounts[uid] = checking

    def update(self):
        result = []

        for uid, checking in list(self.checking_accounts.items()):
            if not checking.thread.done():
                continue

            checking.account.status = checking.thread.result()
            del self.checking_accounts[uid]
            result.append(checking.account)

        if result:
            self.start_checking()

        return result


accounts_manager = _AccountManager()