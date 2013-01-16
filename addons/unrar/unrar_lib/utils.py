# -*- coding: utf-8 -*-
__author__ = 'Esteban Castro Borsani'

import unrar
import models
import cons


def extract_file(path, dest_path=None, password_list=None):
    """
    @path: the rar file path to be extracted
    @dest_path: destination path
    @password_list: a list of password to test
    """
    for pwd in password_list or [None, ]:
        try:
            with OpenRAR(path, cons.RAR_OM_EXTRACT, password=pwd) as fh:
                fh.extract_all(dest_path)
        except unrar.BadPassword:
            continue
        else:
            return
    #if we got here, password was wrong
    raise unrar.BadPassword("Incorrect password")


class OpenRAR:
    """
    usage:
        with OpenRAR("./file.rar", MODE) as fh:
            ...
    """
    def __init__(self, path, mode, password=None):
        self.archive = unrar.RAROpenArchiveDataEx(path, mode, password)
        self.__fh = unrar.RAROpenArchiveEx(self.archive)
        self.fh = models.RARFile(self.__fh, self.archive)

    def __enter__(self): #"yield"
        return self.fh

    def __exit__(self, type, value, traceback):
        #if __init__ raise an exception, this is never reached.
        try:
            unrar.RARCloseArchive(self.__fh)
        except unrar.UnRARError:
            if not traceback:
                raise #re-raise
        if traceback:
            return False #re-raise
        return True
