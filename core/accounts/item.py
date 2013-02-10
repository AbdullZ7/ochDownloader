import uuid


class AccountItem:
    """"""
    def __init__(self, host, username, password, status=None, enable=False):
        """"""
        self.id_account = str(uuid.uuid1())
        self.host = host
        self.username = username
        self.password = password
        self.status = status
        self.enable = enable