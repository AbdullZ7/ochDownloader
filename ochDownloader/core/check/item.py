from core.common.item import uid, get_host_from_url


class CheckingItem:
    # TODO: rename class
    def __init__(self, item):
        self.item = item
        self.thread = None


class CheckItem:

    def __init__(self, url):
        self.uid = uid()
        self.url = url
        self.host = get_host_from_url(url)
        self.name = None
        self.size = 0
        self.status = None
        self.message = None

    @property
    def plugin(self):
        return self.host.replace(".", "_")