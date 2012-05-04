from plugins.uploaded.anonym_download import AnonymDownload as anonym_download
from plugins.uploaded.anonym_download import LinkChecker


class AnonymDownload:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    def add(self):
        return anonym_download(*self.args, **self.kwargs).add()

    def check_link(self, link):
        return anonym_download(*self.args, **self.kwargs).check_link(link)
