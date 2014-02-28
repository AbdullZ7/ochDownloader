import sys
import os
import time
from collections import OrderedDict

from core.api import api
from core import utils
from core.utils.concurrent.thread import Future


class CLI:
    # TODO: wont work with signals... remove and make a non-interactive cli

    def __init__(self):
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.downloads = OrderedDict()

    def run(self):
        while True:
            print("1 {show} | 2 {add} | 0 {exit}".format(show=_("Show Downloads"),
                                                         add=_("Add Downloads"),
                                                         exit=_("exit")))

            line = self.read()
            if line == "1":
                self.show_downloads()
            elif line == "2":
                self.add_downloads()
            elif line == "0":
                sys.exit(0)

            self.clear()

    def read(self):
        return self.stdin.readline().strip()

    def read_int(self):
        try:
            return int(self.read())
        except ValueError:
            return None

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def add_downloads(self):
        self.clear()
        print(_("Add Downloads") + ":")
        print("ex: http://url.com/file.rar http://url.com/file2.rar ...")

        line = self.read()
        links = utils.links_parser(line)

        print(_("Save to path") + ":")
        print("ex: C:/User/Name/MyFolder")

        path = self.read()
        for l in links:
            item = api.create_download_item(url=l, path=path)
            self.downloads[item.uid] = item
            api.downloader.add_to_downloader(item)

    def show_downloads(self):
        while True:
            self.clear()
            print(_("All Downloads") + ":")

            if not self.downloads:
                print(_("No downloads"))
                self.read()
                return

            for i, (uid, item) in enumerate(self.downloads.items()):
                name = item.name or _("Unknown name")
                print(name, item.url)

            print("1 {show} | 2 {start_all} | 3 {remove} | 0 {back}".format(show=_("Show progress"),
                                                                            start_all=_("Start all"),
                                                                            remove=_("Remove download"),
                                                                            back=_("go back")))
            line = self.read()
            if line == "0":
                return
            elif line == "1":
                self.show_progress()
            elif line == "2":
                self.start_all()
            elif line == "3":
                self.remove_download()

    def show_progress(self):
        fu = Future(target=input)

        while True:
            self.clear()
            print(_("Download progress") + ":")

            items = api.downloader.update()
            for i in items:
                print(i.name)
                print(i.progress() + "% completed @" + utils.speed_format(i.speed()))

            print(_("press <Enter> key to go back"))
            time.sleep(1)

            if fu.done():
                return

    def start_all(self):
        uid_list = [i.uid for i in self.downloads.values()]
        api.downloader.start_all(uid_list)

    def remove_download(self):
        print(_("Remove") + ":")

        index = self.read_int()
        if index is None:
            return

        try:
            item_uid = self.downloads.keys()[index]
        except IndexError:
            pass
        else:
            api.downloader.delete([item_uid, ])


if __name__ == '__main__':
    cli = CLI()
    cli.run()