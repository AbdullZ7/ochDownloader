import os
import re
import threading
import logging
logger = logging.getLogger(__name__)

from core.conf_parser import conf

import preferences_gui
from unrar_lib.utils import extract_file
from passwords_handler import passwords_handler

RAR_FILE_PATTERN = '^(?P<name>.*?)(?P<part>\.part\d+)?(?P<ext>\.rar|\.r\d+)$'


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
            if not th.is_alive():
                del self.__th_dict[id_item]
                del self.__item_list[0]
                if self.__item_list:
                    self.start_extract(self.__item_list[0])
            return id_item, th.is_alive(), th.err_msg
        return


class Extract(threading.Thread):
    """"""
    def __init__(self, file_path, dest_path, passwords_list):
        """"""
        threading.Thread.__init__(self)
        self.file_path = file_path
        self.dest_path = dest_path
        self.passwords_list = passwords_list
        self.err_msg = None
        self.daemon = True #exit even if the thread is alive.

    def run(self):
        """"""
        passwords = self.passwords_list or None
        try:
            extract_file(self.file_path, dest_path=self.dest_path, password_list=passwords)
        except Exception as err:
            self.err_msg = str(err)
            logger.exception(err)
        else:
            if conf.get_addon_option(preferences_gui.OPTION_UNRAR_REMOVE_FILES, default=False, is_bool=True):
                self.remove_files()

    def remove_files(self):
        try:
            path, file_name = os.path.split(self.file_path)
            m = re.match(RAR_FILE_PATTERN, file_name)
            name = m.group('name')
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                # check if it's a file and has same name
                if file.startswith(name) and os.path.isfile(file_path):
                    m2 = re.match(RAR_FILE_PATTERN, file)
                    # check if both names matches
                    if m2 is not None and m2.group('name') == name:
                        # check if both are new style xor old style
                        if (m.group('part') is None and m2.group('part') is None) or \
                           (m.group('part') is not None and m2.group('part') is not None):
                            os.remove(file_path)
        except Exception as err:
            logger.exception(err)


if __name__ == "__main__":
    #print Extract(None, None).get_passwords()
    list_a = []
    for _ in list_a or [None, ]:
        print _