import os
import uuid
import threading
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons

import lib as unrar_lib
from lib.rar_exceptions import *
from passwords_handler import passwords_handler

class Item:
    def __init__(self, id_item, file_path, dest_path):
        self.id_item = id_item
        self.file_path = file_path
        self.dest_path = dest_path


class UnRAR:
    """"""
    def __init__(self):
        """"""
        #only single extraction is allowed
        self.__item_list = []
        self.__th_dict = {}
    
    def add(self, file_path, dest_path, id_item):
        """"""
        item = Item(id_item, file_path, dest_path)
        self.__item_list.append(item)
        if not self.__th_dict:
            self.start_extract(item)
    
    def start_extract(self, item):
        passwords_list = passwords_handler.get_passwords()
        th = Extract(item.file_path, item.dest_path, passwords_list)
        self.__th_dict[item.id_item] = th
        th.start()
    
    def get_status(self):
        for id_item, th in self.__th_dict.items():
            if th.complete:
                del self.__th_dict[id_item]
                del self.__item_list[0]
                if self.__item_list:
                    self.start_extract(self.__item_list[0])
            return (id_item, th.complete, th.err_msg)
            #COMPLETE, ERR_MSG = range(2)
        return None


class Extract(threading.Thread):
    """"""
    def __init__(self, file_path, dest_path, passwords_list):
        """"""
        threading.Thread.__init__(self)
        self.file_path = file_path
        self.dest_path = dest_path
        self.passwords_list = passwords_list
        self.complete = False
        self.err_msg = None
        self.daemon = True #exit even if the thread is alive.

    def run(self):
        """"""
        try:
            for pwd in self.passwords_list or [None, ]: #if pwd_list is empty, use [None, ]
                try:
                    unrar_handler = unrar_lib.RarFile(self.file_path, password=pwd)
                    rarinfo_list = unrar_handler.extract(path=self.dest_path, overwrite=True)
                except IncorrectRARPassword as err:
                    self.err_msg = _("Incorrect rar password")
                else:
                    self.err_msg = None
                    break
        except ArchiveHeaderBroken as err:
            self.err_msg = _("Archive header broken")
        except FileOpenError as err:
            self.err_msg = _("File open error")
        except InvalidRARArchiveUsage as err:
            self.err_msg = _("Invalid rar archive usage")
        except Exception as err:
            self.err_msg = _("Unknown error")
            logger.exception(err)
        self.complete =True


if __name__ == "__main__":
    #print Extract(None, None).get_passwords()
    list_a = []
    for _ in list_a or [None, ]:
        print _



