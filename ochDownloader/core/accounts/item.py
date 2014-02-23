from core.common.item import uid


class CheckingAccountItem:

    def __init__(self, item):
        self.item = item
        self.thread = None


class AccountItem:

    def __init__(self, host, username, password, status=None, is_enabled=False):
        self.uid = uid()
        self.host = host
        self.username = username
        self.password = password
        self.status = status
        self.is_enabled = is_enabled

    @property
    def plugin(self):
        return self.host.replace(".", "_")