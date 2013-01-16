# -*- coding: utf-8 -*-
__author__ = 'Esteban Castro Borsani'

import unrar
import cons


class RARFile:
    """"""
    def __init__(self, fh, archive):
        self.fh = fh
        self.archive = archive
        self.header = unrar.RARHeaderDataEx()

    def _read_header(self):
        unrar.RARReadHeaderEx(self.fh, self.header)

    def _process(self, op, path=None, filename=None):
        #process current and go to next index
        unrar.RARProcessFileW(self.fh, op, path, filename)

    def is_password_required(self):
        """
        This operation is only valid after doing extract(), next(), etc
        """
        return self.archive.password_required

    def is_missing_volume(self):
        return self.archive.missing_volume

    def next(self):
        try:
            self._read_header()
            self._process(cons.RAR_SKIP)
        except unrar.EndOfArchive:
            return False
        else:
            return True

    def readfiles(self):
        while self.next():
            yield self.header

    def extract(self, file_list, path=None):
        while True:
            try:
                self._read_header()
                if self.header.file_name in file_list:
                    self._process(cons.RAR_EXTRACT, path)
                else:
                    self._process(cons.RAR_SKIP)
            except unrar.ArchiveOpenError:
                if self.is_missing_volume():
                    raise unrar.ArchiveOpenError("Missing volume")
                else:
                    raise
            except unrar.BadHeaderData:
                if self.is_password_required():
                    raise unrar.BadPassword("Incorrect password")
                else:
                    raise
            except unrar.EndOfArchive:
                return

    def extract_all(self, path=None):
        while True:
            try:
                self._read_header()
                self._process(cons.RAR_EXTRACT, path)
            except unrar.ArchiveOpenError:
                if self.is_missing_volume():
                    raise unrar.ArchiveOpenError("Missing volume")
                else:
                    raise
            except unrar.BadHeaderData:
                if self.is_password_required():
                    raise unrar.BadPassword("Incorrect password")
                else:
                    raise
            except unrar.EndOfArchive:
                return